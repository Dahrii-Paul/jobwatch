import json

from jobwatch import ai, run


def test_screen_and_apply(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "x")
    monkeypatch.setattr(ai, "_call", lambda msgs: json.dumps({"items": [
        {"id": "0", "score": 85, "category": "permanent", "deadline": "2026-12-10", "country": None,
         "reason": "Staff scientist running mass-spec proteomics data analysis"}]}))
    it = {"title": "Staff scientist to BioMS", "url": "u", "context": "", "kw_score": 10, "score": 10,
          "region": "abroad", "category": "permanent"}
    cache = ai.screen([it], run.load_yaml("profile.yaml"), {})
    run.apply_ai(it, cache[ai.cache_key(it)])
    assert it["score"] == round(0.75 * 85 + 0.25 * 10) and it["deadline"] == "2026-12-10" and it["ai"]


def test_screen_survives_http_error(monkeypatch):
    monkeypatch.setenv("LLM_API_KEY", "x")
    def boom(msgs): raise RuntimeError("LLM HTTP 403")
    monkeypatch.setattr(ai, "_call", boom)
    assert ai.screen([{"title": "t", "url": "u"}], run.load_yaml("profile.yaml"), {}) == {}
