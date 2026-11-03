import json

from jobwatch import add_job, fetch, run

BODY = """### Job link

https://www.linkedin.com/jobs/view/12345

### Job title

Postdoc in single-cell genomics, Karolinska Institutet

### Deadline

15 December 2026

### Where

Abroad

### Type

Postdoc

### Notes

_No response_
"""


def test_parse_issue():
    f = add_job.parse_issue(BODY)
    assert f["link"] == "https://www.linkedin.com/jobs/view/12345"
    assert f["title"].startswith("Postdoc in single-cell") and f["notes"] == ""


def _setup(tmp_path, monkeypatch):
    monkeypatch.setattr(run, "DATA", tmp_path)
    monkeypatch.setattr(run, "ROOT", tmp_path)
    monkeypatch.setattr(fetch, "get", lambda *a, **k: (_ for _ in ()).throw(AssertionError("no fetch for linkedin")))
    monkeypatch.setenv("AI_DISABLED", "1")
    monkeypatch.setenv("REPLY_FILE", str(tmp_path / "c.md"))


def test_save_linkedin_job(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    monkeypatch.setenv("ISSUE_BODY", BODY)
    monkeypatch.setenv("ISSUE_NUMBER", "7")
    assert add_job.main() == 0
    jobs = json.loads((tmp_path / "jobs.json").read_text())["jobs"]
    j = jobs[0]
    assert j["saved"] and j["match"] and j["deadline"] == "2026-12-15"
    assert j["category"] == "postdoc" and j["region"] == "abroad" and j["status"] == "open"
    assert "Saved" in (tmp_path / "c.md").read_text()
    # editing the issue (new title) replaces, not duplicates
    monkeypatch.setenv("ISSUE_BODY", BODY.replace("Karolinska Institutet", "KI Stockholm"))
    assert add_job.main() == 0
    jobs = json.loads((tmp_path / "jobs.json").read_text())["jobs"]
    assert len(jobs) == 1 and jobs[0]["title"].endswith("KI Stockholm")


def test_linkedin_without_title_asks(tmp_path, monkeypatch):
    _setup(tmp_path, monkeypatch)
    monkeypatch.setenv("ISSUE_BODY", "### Job link\n\nhttps://x.com/somelab/status/1\n\n### Job title\n\n_No response_\n")
    assert add_job.main() == 1
    assert "fill in" in (tmp_path / "c.md").read_text()
