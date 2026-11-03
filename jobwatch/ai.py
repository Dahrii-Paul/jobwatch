"""Optional AI screening with any OpenAI-compatible chat endpoint.

Default: GitHub Models (free, uses the Actions GITHUB_TOKEN with `models: read`).
Override with env vars:
  LLM_BASE_URL   e.g. https://models.github.ai/inference  (default)
                      https://generativelanguage.googleapis.com/v1beta/openai  (Gemini)
                      https://api.openai.com/v1, https://api.groq.com/openai/v1 ...
  LLM_MODEL      e.g. openai/gpt-4.1-mini (default for GitHub Models)
  LLM_API_KEY    key for that endpoint; falls back to MODEL_TOKEN, then GITHUB_TOKEN
  AI_MAX_CALLS   max requests per run (default 8, each screens up to 12 jobs)
If no key is available, or the endpoint refuses, the agent silently keeps keyword scores.
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import re

from . import fetch

log = logging.getLogger(__name__)

BATCH = 12
CATS = {"permanent", "postdoc", "fellowship", "project", "phd", "other"}

SYSTEM = """You screen academic job adverts for one candidate. Be strict and factual.
For each job return an object:
  id: same id as given
  score: 0-100 fit for the candidate (subject fit AND career stage; 0 = unrelated field)
  category: one of permanent | postdoc | fellowship | project | phd | other
     permanent = regular/tenure(-track) post: Scientist B/C/D..., Assistant/Associate Professor,
                 faculty, lecturer, staff scientist, group leader
     postdoc   = postdoctoral researcher / research associate / research fellow
     fellowship= named postdoctoral fellowship scheme
     project   = JRF/SRF/project scientist/assistant/technician/contract project post
  deadline: application deadline as YYYY-MM-DD if stated in the text, else null (never guess)
  country: country of the post, or null
  reason: <= 18 words on why it does / doesn't fit
Respond ONLY with JSON: {"items": [ ... ]}"""


def _key() -> str | None:
    return os.getenv("LLM_API_KEY") or os.getenv("MODEL_TOKEN") or os.getenv("GITHUB_TOKEN")


def enabled() -> bool:
    return bool(_key()) and os.getenv("AI_DISABLED", "").lower() not in ("1", "true", "yes")


def cache_key(item: dict) -> str:
    raw = "|".join([item.get("url", ""), item.get("title", ""), (item.get("details") or item.get("context") or "")[:400]])
    return hashlib.sha1(raw.encode()).hexdigest()[:16]


def _call(messages: list[dict]) -> str:
    base = os.getenv("LLM_BASE_URL", "https://models.github.ai/inference").rstrip("/")
    model = os.getenv("LLM_MODEL", "openai/gpt-4.1-mini")
    body = {"model": model, "messages": messages, "temperature": 0,
            "response_format": {"type": "json_object"}}
    for attempt in range(2):
        r = fetch.session().post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {_key()}", "Content-Type": "application/json",
                     "Accept": "application/json"},
            json=body, timeout=120,
        )
        try:
            data = r.json()
        except ValueError:
            data = None
        if r.status_code < 400 and data and data.get("choices"):
            return data["choices"][0]["message"]["content"] or ""
        if attempt == 0 and r.status_code in (400, 422) or data is None:
            body.pop("response_format", None)     # some models/endpoints reject it
            continue
        break
    raise RuntimeError(f"LLM HTTP {r.status_code} from {base} ({model}): {r.text[:300]!r}")


def _parse(text: str) -> list[dict]:
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        return []
    try:
        return json.loads(m.group(0)).get("items", [])
    except json.JSONDecodeError:
        return []


def screen(items: list[dict], profile: dict, cache: dict) -> dict:
    """Screen items (not already cached). Updates and returns `cache` {cache_key: verdict}."""
    if not enabled():
        log.info("AI screening disabled (no key)")
        return cache
    todo = [it for it in items if cache_key(it) not in cache]
    max_calls = int(os.getenv("AI_MAX_CALLS", "8"))
    calls = 0
    for i in range(0, len(todo), BATCH):
        if calls >= max_calls:
            log.info("AI budget reached; %d items left for next run", len(todo) - i)
            break
        batch = todo[i:i + BATCH]
        payload = [{
            "id": str(n),
            "title": it["title"],
            "institution_or_site": it.get("source_name"),
            "text": (it.get("details") or it.get("context") or "")[:900],
        } for n, it in enumerate(batch)]
        msgs = [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": "CANDIDATE PROFILE:\n" + profile["summary"].strip()
             + "\n\nJOBS:\n" + json.dumps(payload, ensure_ascii=False)},
        ]
        try:
            verdicts = _parse(_call(msgs))
            calls += 1
        except Exception as e:
            log.warning("AI screening stopped: %s", e)
            break
        for v in verdicts:
            try:
                it = batch[int(v.get("id"))]
            except (TypeError, ValueError, IndexError):
                continue
            cat = v.get("category") if v.get("category") in CATS else None
            dl = v.get("deadline")
            if not (isinstance(dl, str) and re.fullmatch(r"20\d\d-\d\d-\d\d", dl)):
                dl = None
            cache[cache_key(it)] = {
                "score": max(0, min(100, int(v.get("score", 0) or 0))),
                "category": cat, "deadline": dl,
                "country": v.get("country") or None,
                "reason": (v.get("reason") or "")[:160],
            }
    log.info("AI screened %d items in %d calls", sum(1 for it in todo if cache_key(it) in cache), calls)
    return cache
