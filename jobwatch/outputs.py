"""Write the static API (JSON), Atom feed and README stats that GitHub Pages serves."""
from __future__ import annotations

import datetime as dt
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

URGENT_DAYS = 14


def _dump(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=1), "utf-8")


def days_left(job: dict, today: dt.date) -> int | None:
    if not job.get("deadline"):
        return None
    return (dt.date.fromisoformat(job["deadline"]) - today).days


def sort_key(j: dict):
    # open & dated first (soonest deadline), then undated by score
    return (j.get("status") != "open", j.get("deadline") or "9999", -j.get("score", 0))


def write_all(data_dir: Path, db: dict, programs: list, health: list, profile: dict,
              now: dt.datetime, new_ids: list[str]) -> dict:
    today = now.date()
    thr = profile.get("match_threshold", 40)
    jobs = sorted(db.values(), key=sort_key)
    for j in jobs:
        j["match"] = j.get("score", 0) >= thr or bool(j.get("saved"))
        j["new"] = j["id"] in new_ids
    open_match = [j for j in jobs if j["status"] == "open" and j["match"]]
    urgent = [j for j in open_match if (d := days_left(j, today)) is not None and 0 <= d <= URGENT_DAYS]

    meta = {
        "updated": now.isoformat(timespec="minutes"),
        "repo": __import__("os").getenv("GITHUB_REPOSITORY", ""),
        "match_threshold": thr,
        "include_categories": profile.get("include_categories", []),
        "counts": {
            "total_indexed": len(jobs),
            "open_matches": len(open_match),
            "urgent": len(urgent),
            "new_this_run": sum(1 for j in jobs if j["new"] and j["match"]),
            "saved": sum(1 for j in jobs if j.get("saved") and j["status"] == "open"),
            "permanent_india": sum(1 for j in open_match if j["category"] == "permanent" and j["region"] == "india"),
            "postdoc_india": sum(1 for j in open_match if j["category"] in ("postdoc", "fellowship") and j["region"] == "india"),
            "postdoc_abroad": sum(1 for j in open_match if j["category"] in ("postdoc", "fellowship") and j["region"] == "abroad"),
            "permanent_abroad": sum(1 for j in open_match if j["category"] == "permanent" and j["region"] == "abroad"),
            "sources_ok": sum(1 for h in health if h["ok"]),
            "sources_total": len(health),
        },
    }
    _dump(data_dir / "jobs.json", {"meta": meta, "jobs": jobs})
    _dump(data_dir / "open.json", {"meta": meta, "jobs": open_match})
    _dump(data_dir / "urgent.json", {"meta": meta, "jobs": urgent})
    _dump(data_dir / "programs.json", {"meta": meta, "programs": programs})
    _dump(data_dir / "health.json", {"meta": meta, "sources": health})
    _dump(data_dir / "meta.json", meta)
    (data_dir / "feed.xml").write_text(atom(open_match, now), "utf-8")
    return meta


def atom(jobs: list[dict], now: dt.datetime) -> str:
    entries = []
    for j in sorted(jobs, key=lambda j: j.get("first_seen", ""), reverse=True)[:150]:
        dl = f"Deadline {j['deadline']}" if j.get("deadline") else "Deadline: see advert"
        summary = f"[{j['category']}] {j.get('source_name','')} · {j.get('country') or j['region']} · {dl} · score {j['score']}"
        if j.get("ai_reason"):
            summary += f" — {j['ai_reason']}"
        entries.append(f"""  <entry>
    <title>{escape(j['title'])}</title>
    <link href="{escape(j['url'])}"/>
    <id>urn:jobwatch:{j['id']}</id>
    <updated>{j.get('first_seen', now.date().isoformat())}T00:00:00Z</updated>
    <summary>{escape(summary)}</summary>
  </entry>""")
    return f"""<?xml version="1.0" encoding="utf-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <title>JobWatch — Bioinformatics &amp; Computational Biology</title>
  <id>urn:jobwatch:feed</id>
  <updated>{now.astimezone(dt.timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')}</updated>
{chr(10).join(entries)}
</feed>
"""


def update_readme(readme: Path, meta: dict, db: dict, today: dt.date) -> None:
    if not readme.exists():
        return
    c = meta["counts"]
    thr = meta["match_threshold"]
    soon = sorted((j for j in db.values() if j["status"] == "open" and j.get("score", 0) >= thr
                   and (d := days_left(j, today)) is not None and 0 <= d <= 30),
                  key=lambda j: j["deadline"])[:15]
    rows = "\n".join(
        f"| {'🔴' if days_left(j, today) <= 3 else '🟠' if days_left(j, today) <= 10 else '🟡'} **{days_left(j, today)}d** "
        f"| [{j['title'][:90].replace('|', '/')}]({j['url']}) | {j['category']} | {j.get('country') or j['region']} | {j['deadline']} |"
        for j in soon) or "| – | Nothing closing in the next 30 days | | | |"
    block = f"""<!-- STATS:START -->
## Live stats · updated {meta['updated'][:16].replace('T', ' ')}

| Metric | Count |
|---|---|
| 🎯 Open matches | **{c['open_matches']}** |
| 🏛️ Permanent posts — India | **{c['permanent_india']}** |
| 🔬 Postdocs / fellowships — India | **{c['postdoc_india']}** |
| ✈️ Postdocs / fellowships — abroad | **{c['postdoc_abroad']}** |
| 🌍 Permanent / faculty — abroad | **{c['permanent_abroad']}** |
| ⏰ Closing within 14 days | **{c['urgent']}** |
| 🆕 New this run | **{c['new_this_run']}** |
| 📡 Sources working | **{c['sources_ok']} / {c['sources_total']}** |

### ⏳ Closing within 30 days

| Left | Position | Type | Where | Deadline |
|---|---|---|---|---|
{rows}
<!-- STATS:END -->"""
    text = readme.read_text("utf-8")
    text = re.sub(r"<!-- STATS:START -->.*?<!-- STATS:END -->", lambda _: block, text, flags=re.S)
    readme.write_text(text, "utf-8")
