"""Add a job you found yourself (LinkedIn, X, ResearchGate, e-mail, anywhere).

Triggered by the "Save a job" form (a GitHub issue). Reads the issue body from
the ISSUE_BODY env var, saves the job to data/saved.json, republishes the data,
and writes a reply for the issue to comment.md.

    ISSUE_BODY="### Job link\n\nhttps://..." python -m jobwatch.add_job
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re
from pathlib import Path

from bs4 import BeautifulSoup

from . import extract, fetch, run, store

FIELDS = {"job link": "link", "job title": "title", "deadline": "deadline", "where": "where",
          "type": "type", "notes": "notes"}
WHERE = {"india": "india", "abroad": "abroad"}
TYPES = {"permanent": "permanent", "postdoc": "postdoc", "fellowship": "fellowship", "project": "project"}
# sites that never show the advert to a bot — don't bother fetching, rely on what you typed
BLOCKED = re.compile(r"(linkedin\.com|lnkd\.in|x\.com|twitter\.com|t\.co|researchgate\.net|facebook\.com|instagram\.com)", re.I)


def parse_issue(body: str) -> dict:
    out = {}
    for block in re.split(r"^###\s+", body or "", flags=re.M):
        head, _, val = block.partition("\n")
        key = next((v for k, v in FIELDS.items() if head.strip().lower().startswith(k)), None)
        if key:
            val = val.strip()
            out[key] = "" if val in ("_No response_", "None") else val
    if not out.get("link"):                     # plain issue: take the first URL anywhere
        m = re.search(r"https?://\S+", body or "")
        out["link"] = m.group(0) if m else ""
    m = re.search(r"https?://[^\s)>\]]+", out.get("link", ""))
    out["link"] = m.group(0) if m else ""
    return out


def _page_info(url: str) -> tuple[str, str]:
    """(title, text) from the page, or ('', '') when the site blocks bots."""
    if BLOCKED.search(url):
        return "", ""
    try:
        pg = fetch.get(url, timeout=40)
        if pg.status >= 400:
            return "", ""
        if pg.is_pdf:
            first = next((l.strip() for l in pg.text.splitlines() if len(l.strip()) > 15), "")
            return first[:200], pg.text
        soup = BeautifulSoup(pg.text, "lxml")
        og = soup.find("meta", property="og:title")
        title = (og.get("content") if og else "") or (soup.title.get_text(" ", strip=True) if soup.title else "")
        h1 = soup.find("h1")
        if h1 and len(h1.get_text(strip=True)) > 10:
            title = h1.get_text(" ", strip=True)
        return re.sub(r"\s+", " ", title)[:200], extract.page_text(pg.text)
    except Exception:
        return "", ""


def _date(s: str, today: dt.date) -> str | None:
    if not s:
        return None
    if re.fullmatch(r"20\d\d-\d\d-\d\d", s.strip()):
        return s.strip()
    found = extract._dates_in(s, today)
    return found[0][1].isoformat() if found else None


def main() -> int:
    body, issue = os.getenv("ISSUE_BODY", ""), os.getenv("ISSUE_NUMBER")
    reply = Path(os.getenv("REPLY_FILE", "comment.md"))
    today = dt.date.today()
    f = parse_issue(body)
    if not f["link"]:
        reply.write_text("❌ I couldn't find a link in this issue. Edit it and paste the job's URL into **Job link**.")
        return 1

    page_title, text = _page_info(f["link"])
    title = f.get("title") or page_title
    if not title:
        reply.write_text(
            "⚠️ This site doesn't show its pages to bots, so I couldn't read the job title.\n\n"
            "**Edit this issue and fill in *Job title*** (and the deadline if you know it) — "
            "I'll save it as soon as you do.")
        return 1

    notes = f.get("notes", "")
    deadline = (_date(f.get("deadline", ""), today) or extract.find_deadline(text, today)
                or extract.find_deadline(notes, today))
    entry = {
        "url": f["link"], "title": title, "deadline": deadline, "notes": notes,
        "details": run._snippet(text, run.load_yaml("profile.yaml")) if text else "",
        "site": extract.domain(f["link"]), "added": today.isoformat(), "issue": int(issue) if issue else None,
    }
    w = (f.get("where") or "").lower()
    entry["region"] = next((v for k, v in WHERE.items() if k in w), None)
    ty = (f.get("type") or "").lower()
    entry["category"] = next((v for k, v in TYPES.items() if k in ty), None)

    path = run.DATA / "saved.json"
    saved = run._read(path).get("saved", [])
    saved = [s for s in saved if s["url"] != entry["url"]] + [entry]
    path.write_text(json.dumps({"saved": saved}, ensure_ascii=False, indent=1), "utf-8")

    run.main(["--saved-only"])          # republish data + feed with this job included

    jid = store.job_id(entry["url"], entry["title"])
    job = next((j for j in run._read(run.DATA / "jobs.json").get("jobs", []) if j["id"] == jid), {})
    pages = os.getenv("PAGES_URL", "")
    lines = [
        f"✅ Saved **{title}**",
        "",
        f"- Type: **{job.get('category', entry['category'] or '?')}** · Where: **{job.get('country') or job.get('region', '?')}**",
        f"- Deadline: **{deadline or 'not found — edit this issue and add it to get reminders'}**",
        f"- Match with your profile: **{job.get('score', '?')}/100**"
        + (f" — {job['ai_reason']}" if job.get("ai_reason") else ""),
        "",
        f"It's now on your [dashboard]({pages}) and in the feed." if pages else "It's now on your dashboard and in the feed.",
        "To change anything, edit this issue — it will be re-saved.",
    ]
    reply.write_text("\n".join(lines), "utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
