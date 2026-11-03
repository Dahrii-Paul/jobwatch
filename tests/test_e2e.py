"""End-to-end run with the network mocked out."""
import json

from jobwatch import fetch, run

PAGES = {
    "https://icmr.gov.in/recruitment-portal": "tests/fixtures/govt_table.html",
    "https://www.scilifelab.se/careers/?filter=researchers-research-engineers-and-postdocs": "tests/fixtures/cards.html",
}
WP = [{"link": "https://researchersjob.com/research-associate-position-in-rgcb/",
       "title": {"rendered": "Research Associate Position in RGCB, Thiruvananthapuram, Kerala, India"},
       "excerpt": {"rendered": "<p>RA in genomics and NGS data analysis. Last date: 25 November 2026</p>"},
       "date": "2026-10-31T10:00:00"},
      {"link": "https://researchersjob.com/postdoc-gear/",
       "title": {"rendered": "Postdoctoral Researcher in Mechanical Engineering – Örebro University, Sweden"},
       "excerpt": {"rendered": "<p>Gear technology.</p>"}, "date": "2026-11-02T10:00:00"}]
DETAIL_PDF_TEXT = ("Advertisement for Scientist-B (Non-Medical). Disciplines: Bioinformatics, Genomics, "
                   "Microbiology. Last date for online application: 01.12.2026")


def fake_get(url, timeout=30, render=False):
    if url in PAGES:
        return fetch.Page(url, 200, "text/html", open(PAGES[url]).read())
    if url.endswith(".pdf"):
        return fetch.Page(url, 200, "application/pdf", DETAIL_PDF_TEXT, True)
    return fetch.Page(url, 404, "text/html", "")


def test_full_run(tmp_path, monkeypatch):
    monkeypatch.setattr(fetch, "get", fake_get)
    monkeypatch.setattr(fetch, "get_json", lambda url, timeout=30: WP)
    monkeypatch.setattr(run, "DATA", tmp_path)
    monkeypatch.setattr(run, "ROOT", tmp_path)
    (tmp_path / "README.md").write_text("x\n<!-- STATS:START -->\n<!-- STATS:END -->\n")
    rc = run.main(["--only", "icmr", "scilifelab", "researchersjob", "--no-ai", "--no-notify", "--no-programs"])
    assert rc == 0
    jobs = json.loads((tmp_path / "jobs.json").read_text())["jobs"]
    by_title = {j["title"][:30]: j for j in jobs}
    sci = next(j for j in jobs if "Scientist-B" in j["title"])
    assert sci["category"] == "permanent" and sci["region"] == "india"
    assert sci["deadline"] == "2026-12-01" and sci["score"] >= 40      # PDF names Bioinformatics
    ra = next(j for j in jobs if "RGCB" in j["title"])
    assert ra["category"] == "postdoc" and ra["region"] == "india" and ra["deadline"] == "2026-11-25"
    gear = next(j for j in jobs if "Mechanical" in j["title"])
    assert gear["region"] == "abroad" and gear["score"] == 0
    mo = next(j for j in jobs if "multi-omics" in j["title"])
    assert mo["category"] == "postdoc" and mo["country"] == "Sweden" and mo["deadline"] == "2026-11-15"
    driver = next(j for j in jobs if "Driver" in j["title"])
    assert driver["score"] < 40
    readme = (tmp_path / "README.md").read_text()
    assert "Open matches" in readme
    health = json.loads((tmp_path / "health.json").read_text())["sources"]
    assert all(h["ok"] for h in health)
    assert (tmp_path / "feed.xml").read_text().startswith("<?xml")
    # second run: nothing new, first_seen kept
    run.main(["--only", "icmr", "--no-ai", "--no-notify", "--no-programs"])
    jobs2 = json.loads((tmp_path / "jobs.json").read_text())["jobs"]
    assert next(j for j in jobs2 if "Scientist-B" in j["title"])["new"] is False
