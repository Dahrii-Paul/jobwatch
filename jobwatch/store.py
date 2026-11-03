"""Persistent job database (data/jobs.json) with first-seen / last-seen tracking."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
from pathlib import Path

KEEP_DAYS_AFTER_CLOSE = 60     # keep closed posts this long (for the archive view)
UNDATED_OPEN_DAYS = 30         # an undated post counts as open this long after last seen


def job_id(url: str, title: str, listing_url: str = "") -> str:
    base = url if url.rstrip("/") != listing_url.rstrip("/") else url + "|" + title.lower()[:80]
    return hashlib.sha1(base.encode()).hexdigest()[:12]


def load(path: Path) -> dict[str, dict]:
    if path.exists():
        try:
            return {j["id"]: j for j in json.loads(path.read_text("utf-8")).get("jobs", [])}
        except Exception:
            pass
    return {}


def status_of(job: dict, today: dt.date) -> str:
    if job.get("deadline"):
        return "open" if job["deadline"] >= today.isoformat() else "closed"
    last = dt.date.fromisoformat(job.get("last_seen", today.isoformat()))
    return "open" if (today - last).days <= UNDATED_OPEN_DAYS else "stale"


def merge(db: dict[str, dict], fresh: list[dict], today: dt.date) -> tuple[dict, list[dict]]:
    """Merge this run's items into the DB. Returns (db, newly_seen_items)."""
    t = today.isoformat()
    new = []
    for it in fresh:
        old = db.get(it["id"])
        if old:
            keep_first = old.get("first_seen", t)
            # never lose a deadline we found earlier by a later, poorer scrape
            if not it.get("deadline") and old.get("deadline"):
                it["deadline"] = old["deadline"]
            for k in ("details", "ai_reason"):
                if not it.get(k) and old.get(k):
                    it[k] = old[k]
            old.update(it)
            old["first_seen"], old["last_seen"] = keep_first, t
        else:
            it["first_seen"] = it["last_seen"] = t
            db[it["id"]] = it
            new.append(it)
    # refresh status / prune
    for jid in list(db):
        j = db[jid]
        j["status"] = status_of(j, today)
        if j.get("deadline"):
            if (today - dt.date.fromisoformat(j["deadline"])).days > KEEP_DAYS_AFTER_CLOSE:
                del db[jid]
        elif (today - dt.date.fromisoformat(j["last_seen"])).days > 120:
            del db[jid]
    return db, new
