"""Save a batch of jobs sent from an e-mail alert (the Gmail → LinkedIn bridge).

The Gmail script sends a GitHub `repository_dispatch` event whose payload is
    {"jobs": [{"url", "title", "company", "location", "via"}...]}
The workflow passes it in ALERT_PAYLOAD; this saves the jobs to data/saved.json
and republishes the dashboard and feed.

LinkedIn alerts carry no deadline, so each job expires EXPIRE_DAYS after it arrives.
"""
from __future__ import annotations

import datetime as dt
import json
import os
import re

from . import run

EXPIRE_DAYS = 30
MAX_PER_BATCH = 100


def canonical(url: str) -> str:
    """https://www.linkedin.com/comm/jobs/view/4012345678/?trk=... → .../jobs/view/4012345678/"""
    m = re.search(r"linkedin\.com/(?:comm/)?jobs/view/(\d+)", url or "")
    return f"https://www.linkedin.com/jobs/view/{m.group(1)}/" if m else (url or "").split("?")[0]


def save(jobs: list[dict], today: dt.date) -> int:
    path = run.DATA / "saved.json"
    saved = run._read(path).get("saved", [])
    by_url = {s["url"]: s for s in saved}
    added = 0
    for j in jobs[:MAX_PER_BATCH]:
        url, title = canonical(j.get("url", "")), (j.get("title") or "").strip()
        if not url.startswith("http") or len(title) < 4:
            continue
        company, location = (j.get("company") or "").strip(), (j.get("location") or "").strip()
        full_title = f"{title} — {company}" if company and company.lower() not in title.lower() else title
        if url in by_url:                      # seen again in a newer alert: keep it alive
            by_url[url]["expires"] = (today + dt.timedelta(days=EXPIRE_DAYS)).isoformat()
            continue
        by_url[url] = {
            "url": url, "title": full_title[:240], "deadline": None,
            "notes": " · ".join(x for x in (company, location) if x),
            "site": "LinkedIn", "added": today.isoformat(),
            "expires": (today + dt.timedelta(days=EXPIRE_DAYS)).isoformat(),
            "via": j.get("via") or "linkedin-alert",
        }
        added += 1
    # forget alert jobs a month after they expired; keep everything you saved by hand
    cutoff = (today - dt.timedelta(days=30)).isoformat()
    kept = [s for s in by_url.values() if s.get("via", "manual") == "manual" or (s.get("expires") or "9999") >= cutoff]
    path.write_text(json.dumps({"saved": kept}, ensure_ascii=False, indent=1), "utf-8")
    return added


def main() -> int:
    payload = json.loads(os.getenv("ALERT_PAYLOAD") or "{}")
    jobs = payload.get("jobs") or []
    n = save(jobs, dt.date.today())
    print(f"Received {len(jobs)} jobs from e-mail alerts, {n} new")
    run.main(["--saved-only"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
