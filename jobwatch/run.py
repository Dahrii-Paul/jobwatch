"""JobWatch agent — one full run.

    python -m jobwatch.run                 # everything
    python -m jobwatch.run --only icmr dbt # just some sources
    python -m jobwatch.run --no-ai --no-notify
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import logging
import os
import re
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from . import ai, classify, extract, fetch, notify, outputs, store

ROOT = Path(__file__).resolve().parent.parent
CONFIG, DATA = ROOT / "config", ROOT / "data"
log = logging.getLogger("jobwatch")

WP_SEARCH_TERMS = ["bioinformatics", "computational biology", "genomics", "NGS",
                   "scientist recruitment", "assistant professor", "postdoctoral bioinformatics"]


def load_yaml(name: str) -> dict:
    return yaml.safe_load((CONFIG / name).read_text("utf-8"))


# ───────────────────────── collect listings ─────────────────────────

def _collect_wordpress(src: dict) -> tuple[list[dict], str]:
    base = src["urls"][0].rstrip("/")
    items, err = [], ""
    try:
        for term in src.get("wp_search", WP_SEARCH_TERMS):
            q = term.replace(" ", "+")
            posts = fetch.get_json(f"{base}/wp-json/wp/v2/posts?search={q}&per_page=40"
                                   f"&_fields=link,title,date,excerpt")
            items += extract.from_wp_json(posts)
        if items:
            return items, f"{base}/wp-json"
    except Exception as e:
        err = f"wp-json: {e}"
    feeds = [f"{base}/{c.strip('/')}/feed/" for c in src.get("wp_categories", [])] or [f"{base}/feed/"]
    for f in feeds:
        try:
            pg = fetch.get(f)
            if pg.status < 400:
                items += extract.from_rss(pg.text)
        except Exception as e:
            err = f"{err}; feed: {e}"
    if not items:
        raise RuntimeError(err or "no posts found")
    return items, feeds[0]


def collect(src: dict) -> tuple[list[dict], dict]:
    t0 = time.time()
    h = {"id": src["id"], "name": src["name"], "region": src.get("region"), "verified": src.get("verified", False),
         "ok": False, "count": 0, "url": src["urls"][0], "error": ""}
    items: list[dict] = []
    try:
        if src.get("type") == "wordpress":
            items, h["url"] = _collect_wordpress(src)
        else:
            errors = []
            for url in src["urls"]:
                try:
                    pg = fetch.get(url, render=src.get("render", False))
                except Exception as e:
                    errors.append(f"{url}: {type(e).__name__}")
                    continue
                if pg.status >= 400:
                    errors.append(f"{url}: HTTP {pg.status}")
                    continue
                if src.get("type") == "rss" or pg.text.lstrip().startswith("<?xml"):
                    items = extract.from_rss(pg.text)
                else:
                    items = extract.from_html(pg.text, pg.url, src.get("link_pattern"))
                h["url"] = pg.url
                if items:
                    break
                errors.append(f"{url}: 0 job-like links")
            h["error"] = "; ".join(errors) if not items else ""
        h["ok"] = bool(items)
    except Exception as e:
        h["error"] = f"{type(e).__name__}: {e}"[:300]
    h["count"] = len(items)
    h["seconds"] = round(time.time() - t0, 1)
    for it in items:
        it["listing_url"] = h["url"]
    return items, h


# ───────────────────────── enrich + score ─────────────────────────

def _snippet(text: str, profile: dict) -> str:
    """Opening text + sentences mentioning the candidate's subjects (for the AI and the dashboard)."""
    words = [w.lower() for w in profile["core_keywords"]]
    sents = re.split(r"(?<=[.;:])\s+", text)
    hits = [s for s in sents if any(w in s.lower() for w in words)][:4]
    return (text[:450] + (" … " + " … ".join(hits) if hits else ""))[:1100]


def enrich(item: dict, profile: dict, today: dt.date) -> None:
    """Open the job page (or PDF advert) to find deadline & subject details."""
    try:
        pg = fetch.get(item["url"], timeout=40)
        if pg.status >= 400:
            return
        text = pg.text if pg.is_pdf else extract.page_text(pg.text)
        dl = extract.find_deadline(text, today)
        if not dl and not pg.is_pdf:
            pdfs = extract.pdf_links(pg.text, pg.url)[:1]
            for p in pdfs:
                pp = fetch.get(p, timeout=40)
                if pp.is_pdf and pp.text:
                    text += " " + pp.text
                    dl = extract.find_deadline(pp.text, today)
        if text.strip():
            item["details"] = _snippet(text, profile)
        if dl and not item.get("deadline"):
            item["deadline"] = dl
        item["details_checked"] = True
    except Exception as e:
        log.debug("detail fetch failed %s: %s", item["url"], e)


def build_item(raw: dict, src: dict, profile: dict, today: dt.date) -> dict:
    it = {
        "id": store.job_id(raw["url"], raw["title"], raw.get("listing_url", "")),
        "title": raw["title"], "url": raw["url"], "context": raw.get("context", "")[:600],
        "source_id": src["id"], "source_name": src["name"], "published": raw.get("published"),
    }
    it["deadline"] = extract.find_deadline(f"{raw['title']} {raw.get('context', '')}", today)
    return it


def classify_item(it: dict, src: dict, profile: dict) -> None:
    text = f"{it['title']} {it.get('context', '')} {it.get('details', '')}"
    it["category"] = classify.categorise(it["title"], f"{it.get('context','')} {it.get('details','')}",
                                         src.get("default_category"))
    it["contract"] = classify.is_contract(it["title"])
    it["region"], country = classify.region_country(text, src)
    it["country"] = it.get("country") or country
    s = classify.score(it, profile, src)
    it["kw_score"], it["matched"], it["check_advt"] = s["score"], s["matched"], s["check_advt"]
    it["score"] = s["score"]
    coi = [c.lower() for c in profile.get("countries_of_interest") or []]
    if coi and it["region"] == "abroad" and it["country"] and it["country"].lower() not in coi:
        it["score"] = max(0, it["score"] - 30)


def apply_ai(it: dict, verdict: dict) -> None:
    it["score"] = round(0.75 * verdict["score"] + 0.25 * it["kw_score"])
    if verdict.get("category"):
        it["category"] = verdict["category"]
    if verdict.get("deadline") and not it.get("deadline"):
        it["deadline"] = verdict["deadline"]
    if verdict.get("country") and it["region"] == "abroad" and not it.get("country"):
        it["country"] = verdict["country"]
    it["ai_reason"] = verdict.get("reason", "")
    it["ai"] = True


# ───────────────────────── programmes ─────────────────────────

def check_programs(today: dt.date) -> tuple[list[dict], list[dict]]:
    progs, health = load_yaml("programs.yaml")["programs"], []

    def one(p):
        p = dict(p, deadline=None, status="check", checked=today.isoformat())
        try:
            pg = fetch.get(p["url"], timeout=40)
            if pg.status < 400:
                text = pg.text if pg.is_pdf else extract.page_text(pg.text)
                dl = extract.find_deadline(text, today)
                if dl and dl >= today.isoformat():
                    p["deadline"], p["status"] = dl, "open"
                elif dl:
                    p["last_deadline"], p["status"] = dl, "closed"
                p["ok"] = True
            else:
                p["ok"], p["error"] = False, f"HTTP {pg.status}"
        except Exception as e:
            p["ok"], p["error"] = False, type(e).__name__
        return p

    with ThreadPoolExecutor(6) as ex:
        out = list(ex.map(one, progs))
    for p in out:
        health.append({"id": "prog:" + p["id"], "name": p["name"], "region": p["region"], "ok": p["ok"],
                       "count": 1 if p["ok"] else 0, "url": p["url"], "error": p.get("error", ""),
                       "verified": False, "seconds": 0})
    return out, health


# ───────────────────────── main ─────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="JobWatch agent")
    ap.add_argument("--only", nargs="*", help="source ids to run")
    ap.add_argument("--no-ai", action="store_true")
    ap.add_argument("--no-details", action="store_true")
    ap.add_argument("--no-notify", action="store_true")
    ap.add_argument("--no-programs", action="store_true")
    ap.add_argument("-v", "--verbose", action="store_true")
    a = ap.parse_args(argv)
    logging.basicConfig(level=logging.DEBUG if a.verbose else logging.INFO,
                        format="%(asctime)s %(levelname)s %(message)s", datefmt="%H:%M:%S")

    now = dt.datetime.now(ZoneInfo(os.getenv("JOBWATCH_TZ", "Asia/Kolkata")))
    today = now.date()
    profile = load_yaml("profile.yaml")
    sources = [s for s in load_yaml("sources.yaml")["sources"] if s.get("enabled", True)]
    if a.only:
        sources = [s for s in sources if s["id"] in a.only]
    db = store.load(DATA / "jobs.json")

    # 1. collect listings (plain sites in parallel, browser-rendered ones sequentially)
    plain = [s for s in sources if not s.get("render")]
    rendered = [s for s in sources if s.get("render")]
    with ThreadPoolExecutor(8) as ex:
        results = list(ex.map(collect, plain))
    results += [collect(s) for s in rendered]
    fetch.close()

    health, items = [], []
    for src, (raws, h) in zip(plain + rendered, results):
        health.append(h)
        log.info("%-18s %3d items %s", src["id"], h["count"], ("✗ " + h["error"]) if h["error"] else "")
        seen = set()
        for raw in raws:
            it = build_item(raw, src, profile, today)
            if it["id"] in seen:
                continue
            seen.add(it["id"])
            old = db.get(it["id"])
            if old and old.get("details_checked"):       # reuse earlier page visit
                it["details"], it["details_checked"] = old.get("details"), True
                it["deadline"] = it["deadline"] or old.get("deadline")
            classify_item(it, src, profile)
            it["_src"] = src
            items.append(it)

    # 2. open promising job pages / PDFs for deadline + subject (budgeted)
    if not a.no_details:
        budget = int(os.getenv("MAX_DETAIL_FETCHES", "200"))
        per_src: dict[str, int] = {}
        todo = []
        for it in sorted(items, key=lambda x: -x["score"]):
            src = it["_src"]
            if it.get("details_checked") or not src.get("follow_details", True):
                continue
            if it["category"] in ("phd",) or (it["score"] < 10 and not it["check_advt"]):
                continue
            if it.get("deadline") and it["score"] >= 60 and not it["check_advt"]:
                continue
            if per_src.get(src["id"], 0) >= 15 or len(todo) >= budget:
                continue
            per_src[src["id"]] = per_src.get(src["id"], 0) + 1
            todo.append(it)
        log.info("Opening %d job pages for details", len(todo))
        with ThreadPoolExecutor(8) as ex:
            list(ex.map(lambda it: enrich(it, profile, today), todo))
        for it in todo:
            classify_item(it, it["_src"], profile)

    # 3. AI screening (optional, cached)
    cache_path = DATA / "ai_cache.json"
    cache = json.loads(cache_path.read_text()) if cache_path.exists() else {}
    if not a.no_ai:
        cand = sorted([it for it in items if (it["score"] >= 15 or it["check_advt"]) and it["category"] != "phd"],
                      key=lambda x: -x["score"])
        cache = ai.screen(cand, profile, cache)
        cache_path.write_text(json.dumps(cache, indent=0), "utf-8")
    for it in items:
        v = cache.get(ai.cache_key(it))
        if v:
            apply_ai(it, v)

    # 4. merge, publish
    for it in items:
        it.pop("_src", None)
    db, new = store.merge(db, items, today)
    programs, p_health = ([], []) if a.no_programs else check_programs(today)
    meta = outputs.write_all(DATA, db, programs, health + p_health, profile, now, [j["id"] for j in new])
    outputs.update_readme(ROOT / "README.md", meta, db, today)

    # 5. alert on new matches
    inc = set(profile.get("include_categories", []))
    new_matches = [j for j in new if j.get("score", 0) >= profile.get("match_threshold", 40)
                   and j["category"] in inc and j["status"] == "open"]
    log.info("Done: %d items this run, %d new, %d new matches", len(items), len(new), len(new_matches))
    if new_matches and not a.no_notify:
        pages = os.getenv("PAGES_URL")
        notify.github_issue(new_matches, pages)
        notify.telegram(new_matches)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
