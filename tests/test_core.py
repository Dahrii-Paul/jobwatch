import datetime as dt
import json

import pytest

from jobwatch import classify, extract, run

TODAY = dt.date(2026, 11, 3)
PROFILE = run.load_yaml("profile.yaml")


@pytest.mark.parametrize("text,expected", [
    ("Application deadline: November 9, 2026 Read", "2026-11-09"),
    ("Last Date: 30.11.2026 (5:00 PM)", "2026-11-30"),
    ("Recruitment of Scientist at NIAB, Govt. of India: Apply by 30 November 2026", "2026-11-30"),
    ("Closes 01 Nov", "2026-11-01"),
    ("Last date 10/12/2026; Last date extended upto 20th December, 2026", "2026-12-20"),
    ("Published on 2026-10-01. Deadline 2026-12-15", "2026-12-15"),
    ("Posted October 2, 2026 for a postdoc", None),
])
def test_deadline(text, expected):
    assert extract.find_deadline(text, TODAY) == expected


@pytest.mark.parametrize("title,cat", [
    ("Advertisement for 30 vacancies of Scientist-B at ICMR Headquarters", "permanent"),
    ("Regular Assistant Professor Position in IIIT Pune", "permanent"),
    ("Postdoc in multi-omics machine learning and computational cancer biology", "postdoc"),
    ("Research Associate Position in RGCB, Thiruvananthapuram", "postdoc"),
    ("Project Scientist Position at IISER Bhopal", "project"),
    ("PhD position in Molecular Biology", "phd"),
    ("Recruitment of JRF and Project Assistant at IIT Madras", "junior"),
    ("Institute Postdoctoral Fellow in Computational Biology, IISc", "postdoc"),
    ("Staff scientist to BioMS", "permanent"),
    ("Associate Senior Lecturer (SciLifeLab Fellow) in Antimicrobial Resistance", "permanent"),
    ("DBT Ramalingaswami Re-entry Fellowship 2026", "fellowship"),
    ("Research Fellow in Bioinformatics (ITD-DIB-2026-04)", "postdoc"),
    ("Project Research Scientist-I (Biostatistics)", "project"),
    ("Project Research Scientist at RGCB, Thiruvananthapuram", "project"),
])
def test_category(title, cat):
    assert classify.categorise(title) == cat


def test_score_relevant_vs_not():
    src = {"region": "abroad"}
    good = {"title": "Postdoc in single-cell genomics and bioinformatics", "category": "postdoc"}
    bad = {"title": "Postdoctoral Researcher in Mechanical Engineering with a Focus on Gear Technology", "category": "postdoc"}
    assert classify.score(good, PROFILE, src)["score"] >= 60
    assert classify.score(bad, PROFILE, src)["score"] == 0


def test_life_science_permanent_flag():
    src = {"region": "india", "life_science": True}
    it = {"title": "Advertisement for 30 vacancies of Scientist-B at ICMR", "category": "permanent"}
    s = classify.score(it, PROFILE, src)
    assert s["check_advt"] and s["score"] >= 30


def test_region_mixed():
    src = {"region": "mixed"}
    assert classify.region_country("Research Associate Position at IIT Gandhinagar: India", src)[0] == "india"
    assert classify.region_country("Postdoc at KTH Royal Institute of Technology, Sweden", src) == ("abroad", "Sweden")


def test_html_listing_table():
    html = open("tests/fixtures/govt_table.html").read()
    items = extract.from_html(html, "https://icmr.gov.in/recruitment-portal")
    titles = [i["title"] for i in items]
    assert any("Scientist-B" in t for t in titles)
    assert not any(t.lower().startswith("view") for t in titles)
    sci = next(i for i in items if "Scientist-B" in i["title"])
    assert extract.find_deadline(sci["title"] + " " + sci["context"], TODAY) == "2026-12-01"


def test_html_cards():
    html = open("tests/fixtures/cards.html").read()
    items = extract.from_html(html, "https://www.scilifelab.se/careers/", "/career/")
    assert len(items) == 2   # PhD-only card has no job words → dropped
    pd = next(i for i in items if "multi-omics" in i["title"])
    assert extract.find_deadline(pd["title"] + " " + pd["context"], TODAY) == "2026-11-15"


def test_result_notices_dropped():
    html = """<ul><li><a href="/r.pdf">Result for Research Scientist of RN No THS/RN/20/2026</a></li>
    <li><a href="/s.pdf">Shortlisted candidates for Scientist-C interview</a></li>
    <li><a href="/a.pdf">Advertisement for Scientist-C (Computational Biology) posts</a></li></ul>"""
    titles = [i["title"] for i in extract.from_html(html, "https://thsti.res.in/")]
    assert titles == ["Advertisement for Scientist-C (Computational Biology) posts"]


def test_careers_link_discovery():
    html = '<a href="/">Home</a><a href="/about">About us</a><a href="/careers">Careers</a><a href="/rti">RTI</a>'
    assert extract.careers_links(html, "https://www.iitp.ac.in/") == ["https://www.iitp.ac.in/careers"]


def test_navigation_and_news_dropped():
    html = """<ul><li><a href="/c/bio">Bioinformatics & Computational Biology 11</a></li>
    <li><a href="/n/1">African genomics leaders meet in Pretoria to advance public health</a></li>
    <li><a href="/j/1">Postdoctoral Fellow in Computational Biology</a></li></ul>"""
    assert [i["title"] for i in extract.from_html(html, "https://zoombio.org/")] == ["Postdoctoral Fellow in Computational Biology"]
