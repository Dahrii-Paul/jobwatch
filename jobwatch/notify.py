"""Alerts for newly found matches.

* GitHub Issue digest (on by default inside Actions): GitHub e-mails you about new
  issues in repos you watch, so this doubles as an e-mail alert with zero setup.
* Telegram (optional): set repo secrets TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID.
"""
from __future__ import annotations

import logging
import os

from . import fetch

log = logging.getLogger(__name__)

ICON = {"permanent": "🏛️", "postdoc": "🔬", "fellowship": "🎓", "project": "🧪", "phd": "📘", "other": "📄"}


def _line(j: dict, md: bool = True) -> str:
    dl = j.get("deadline") or "see advert"
    where = j.get("country") or j.get("region", "")
    if md:
        return f"- {ICON.get(j['category'], '📄')} [{j['title']}]({j['url']}) — {j.get('source_name','')} · {where} · **deadline {dl}** · score {j['score']}"
    return f"{ICON.get(j['category'], '📄')} {j['title']}\n{j.get('source_name','')} · {where} · deadline {dl}\n{j['url']}"


def github_issue(new_matches: list[dict], pages_url: str | None) -> None:
    token, repo = os.getenv("GITHUB_TOKEN"), os.getenv("GITHUB_REPOSITORY")
    if not (token and repo) or not new_matches or os.getenv("ISSUE_ALERTS", "true").lower() == "false":
        return
    groups = {}
    for j in new_matches:
        key = ("India" if j["region"] == "india" else "Abroad") + " · " + j["category"]
        groups.setdefault(key, []).append(j)
    body = [f"**{len(new_matches)} new matching opportunities**" + (f" · [Open dashboard]({pages_url})" if pages_url else ""), ""]
    for g in sorted(groups):
        body += [f"### {g}", *[_line(j) for j in sorted(groups[g], key=lambda x: x.get('deadline') or '9999')], ""]
    body.append("_Close this issue once you've reviewed it._")
    title = f"🔔 {len(new_matches)} new jobs — " + new_matches[0].get("first_seen", "")
    r = fetch.session().post(
        f"https://api.github.com/repos/{repo}/issues",
        headers={"Authorization": f"Bearer {token}", "Accept": "application/vnd.github+json"},
        json={"title": title, "body": "\n".join(body)[:60000], "labels": ["job-alert"]},
        timeout=30,
    )
    if r.status_code >= 300:
        log.warning("Issue alert failed: %s %s", r.status_code, r.text[:200])


def telegram(new_matches: list[dict]) -> None:
    token, chat = os.getenv("TELEGRAM_BOT_TOKEN"), os.getenv("TELEGRAM_CHAT_ID")
    if not (token and chat) or not new_matches:
        return
    chunks, cur = [], f"🔔 {len(new_matches)} new matching jobs\n\n"
    for j in new_matches:
        line = _line(j, md=False) + "\n\n"
        if len(cur) + len(line) > 3800:
            chunks.append(cur)
            cur = ""
        cur += line
    chunks.append(cur)
    for c in chunks:
        try:
            fetch.session().post(f"https://api.telegram.org/bot{token}/sendMessage",
                                 json={"chat_id": chat, "text": c, "disable_web_page_preview": True}, timeout=30)
        except Exception as e:
            log.warning("Telegram failed: %s", e)
