import datetime as dt
import json

from jobwatch import run, save_alerts

JOBS = [
    {"url": "https://www.linkedin.com/comm/jobs/view/4012345678/?trackingId=abc", "title": "Postdoctoral Fellow - Computational Genomics",
     "company": "Indian Institute of Science (IISc)", "location": "Bengaluru, Karnataka, India", "via": "linkedin-alert"},
    {"url": "https://www.linkedin.com/comm/jobs/view/4012340000/?trackingId=ghi", "title": "Senior Data Analyst",
     "company": "Some Bank Ltd", "location": "Mumbai, Maharashtra, India", "via": "linkedin-alert"},
]


def test_alert_jobs_saved_scored_and_expire(tmp_path, monkeypatch):
    monkeypatch.setattr(run, "DATA", tmp_path)
    monkeypatch.setattr(run, "ROOT", tmp_path)
    monkeypatch.setenv("AI_DISABLED", "1")
    monkeypatch.setenv("ALERT_PAYLOAD", json.dumps({"jobs": JOBS + JOBS}))   # duplicates ignored
    assert save_alerts.main() == 0
    saved = json.loads((tmp_path / "saved.json").read_text())["saved"]
    assert [s["url"] for s in saved] == ["https://www.linkedin.com/jobs/view/4012345678/",
                                         "https://www.linkedin.com/jobs/view/4012340000/"]
    jobs = {j["title"]: j for j in json.loads((tmp_path / "jobs.json").read_text())["jobs"]}
    pd = jobs["Postdoctoral Fellow - Computational Genomics — Indian Institute of Science (IISc)"]
    assert pd["match"] and pd["category"] == "postdoc" and pd["region"] == "india" and pd["via"] == "linkedin-alert"
    bank = jobs["Senior Data Analyst — Some Bank Ltd"]
    assert not bank["match"]                      # alert jobs must still fit your profile
    # 31 days later an undated alert job is closed
    from jobwatch import store
    assert store.status_of(dict(pd, expires=(dt.date.today() - dt.timedelta(days=1)).isoformat()), dt.date.today()) == "closed"


def test_shared_x_post(tmp_path, monkeypatch):
    monkeypatch.setattr(run, "DATA", tmp_path)
    monkeypatch.setattr(run, "ROOT", tmp_path)
    monkeypatch.setenv("AI_DISABLED", "1")
    post = {"url": "https://x.com/ncbs/status/123456", "title": "Postdoc in TB genomics, NCBS — apply by 30 Nov 2026",
            "company": "", "location": "Join our lab!", "via": "email-share"}
    monkeypatch.setenv("ALERT_PAYLOAD", json.dumps({"jobs": [post]}))
    assert save_alerts.main() == 0
    j = json.loads((tmp_path / "jobs.json").read_text())["jobs"][0]
    assert j["match"] and j["saved"] and j["deadline"] == "2026-11-30" and j["via"] == "manual" and not j.get("expires")
