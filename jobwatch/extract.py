"""Turn listing pages (HTML / RSS / WordPress) into candidate job items, and find deadlines."""
from __future__ import annotations

import datetime as dt
import html as htmllib
import re
from urllib.parse import urljoin, urldefrag, urlparse

from bs4 import BeautifulSoup
from lxml import etree

# ───────────────────────── candidate extraction ─────────────────────────

JOB_WORDS = re.compile(
    r"post-?doc|post[\s-]?doctoral|scientist|professor|faculty|lecturer|fellow|"
    r"research associate|\bRA[\s-]?(?:I{1,3}|[123])\b|recruit|vacanc|position|advertisement|\badvt\b|"
    r"opening|hiring|group leader|investigator|researcher|bioinformatic|computational|genomic|"
    r"walk[\s-]?in|interview|appointment|engagement of",
    re.I,
)
GENERIC_LINK_TEXT = re.compile(
    r"^(view|download|read( more)?|more|details?|apply( now| online| here)?|click here|here|link|pdf|"
    r"notification|advertisement|advt\.?|corrigendum|addendum|english|hindi|open|\W*)"
    r"(\s*\(?[\d.,]+\s*(kb|mb)\)?)?\s*$",
    re.I,
)
NOT_A_JOB = re.compile(
    r"^\s*(shortlisted|short[\s-]?list|list of|result|final result|selection list|selected candidates|"
    r"answer key|admit card|call letter|minutes|marks|merit list|interview schedule|schedule of interview|"
    r"status of|rejected|provisional|cancell?ation|tender|quotation|eoi\b)",
    re.I,
)
SKIP_HREF = re.compile(r"^(#|javascript:|mailto:|tel:|whatsapp:)", re.I)
SKIP_URL = re.compile(
    r"(facebook|twitter|x\.com|linkedin|instagram|youtube|t\.me|whatsapp)\.|/(login|signin|register|"
    r"privacy|cookie|terms|sitemap|contact|accessibility|feedback|rti|tender)s?\b",
    re.I,
)
BLOCK_TAGS = ("tr", "li", "article", "dd", "section")


def _clean(s: str) -> str:
    return re.sub(r"\s+", " ", htmllib.unescape(s or "")).strip()


def _row_context(tr) -> tuple[str, str]:
    """For a table row: ('Header: value | ...', longest descriptive cell)."""
    cells = tr.find_all(["td", "th"], recursive=False)
    vals = [_clean(c.get_text(" ", strip=True)) for c in cells]
    headers: list[str] = []
    table = tr.find_parent("table")
    if table is not None:
        hrow = table.find("tr")
        if hrow is not None and hrow is not tr and hrow.find("th"):
            headers = [_clean(c.get_text(" ", strip=True)) for c in hrow.find_all(["th", "td"], recursive=False)]
    parts = []
    for i, v in enumerate(vals):
        if not v:
            continue
        h = headers[i] if i < len(headers) else ""
        parts.append(f"{h}: {v}" if h else v)
    title = max((v for v in vals if not re.fullmatch(r"[\d\s.|-]*", v) and not GENERIC_LINK_TEXT.match(v)),
                key=len, default="")
    return " | ".join(parts)[:900], title


def _context_for(a) -> str:
    """Text of the nearest row/list-item/card around a link (gives deadline, institute...).
    Stops climbing before reaching a container that holds other jobs' links."""
    tr = a.find_parent("tr")
    if tr is not None:
        return _row_context(tr)[0]
    best = _clean(a.get_text(" ", strip=True))
    node = a
    for _ in range(5):
        parent = node.parent
        if parent is None or parent.name in ("body", "html", "[document]"):
            break
        hrefs = {x.get("href") for x in parent.find_all("a", href=True)}
        if len(hrefs) > 2:
            break
        txt = _clean(parent.get_text(" ", strip=True))
        if len(txt) > 900:
            break
        node, best = parent, txt
        if node.name in BLOCK_TAGS:
            break
    return best[:900]


def from_html(html: str, base_url: str, link_pattern: str | None = None,
              require_job_words: bool = True) -> list[dict]:
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "noscript", "nav", "header", "footer", "form", "svg"]):
        t.decompose()
    pat = re.compile(link_pattern, re.I) if link_pattern else None
    out: dict[str, dict] = {}
    for a in soup.find_all("a", href=True):
        href = a["href"].strip()
        if not href or SKIP_HREF.match(href):
            continue
        url = urldefrag(urljoin(base_url, href))[0]
        if not url.startswith("http") or SKIP_URL.search(url):
            continue
        if pat and not pat.search(url):
            continue
        text = _clean(a.get_text(" ", strip=True)) or _clean(a.get("title", ""))
        context = _context_for(a)
        title = text
        if len(title) < 12 or GENERIC_LINK_TEXT.match(title):
            # Link text is "View (470 KB)" etc. → take the row / card text instead
            tr = a.find_parent("tr")
            if tr is not None:
                title = _row_context(tr)[1]
            else:
                title = re.sub(re.escape(text), "", context, flags=re.I).strip(" |-:") if text else context
        title = re.sub(r"^\d+\s*[|.)]\s*", "", title)               # drop "34 |" serial numbers
        title = re.sub(r"\s+(application deadline|deadline|closing date|last date|closes)\b.*$", "", title, flags=re.I)
        title = re.sub(r"\s+(read( more)?|apply( now)?|more)$", "", title, flags=re.I)[:260]
        if len(title) < 12:
            continue
        if NOT_A_JOB.search(title):
            continue
        if require_job_words and not JOB_WORDS.search(title + " " + context):
            continue
        key = url if url.rstrip("/") != base_url.rstrip("/") else url + "#" + title[:60]
        if key in out:            # keep the richer context
            if len(context) > len(out[key]["context"]):
                out[key]["context"] = context
            continue
        out[key] = {"title": title, "url": url, "context": context if context != title else ""}
    return list(out.values())


def from_rss(xml_text: str) -> list[dict]:
    """Parse RSS 2.0 or Atom without extra dependencies."""
    items = []
    try:
        root = etree.fromstring(xml_text.encode("utf-8", "ignore"),
                                parser=etree.XMLParser(recover=True, resolve_entities=False))
    except Exception:
        return items
    if root is None:
        return items
    for it in root.iter("item", "{http://www.w3.org/2005/Atom}entry"):
        def first(*names):
            for n in names:
                el = it.find(n)
                if el is not None:
                    return el
            return None
        t = first("title", "{http://www.w3.org/2005/Atom}title")
        l = first("link", "{http://www.w3.org/2005/Atom}link")
        d = first("description", "{http://www.w3.org/2005/Atom}summary", "{http://www.w3.org/2005/Atom}content")
        p = first("pubDate", "{http://www.w3.org/2005/Atom}published", "{http://www.w3.org/2005/Atom}updated")
        link = (l.get("href") if l is not None and l.get("href") else (l.text if l is not None else "")) or ""
        desc = BeautifulSoup(d.text or "", "lxml").get_text(" ", strip=True) if d is not None else ""
        if t is None or not link:
            continue
        items.append({"title": _clean(t.text or "")[:260], "url": link.strip(),
                      "context": _clean(desc)[:900], "published": _parse_any_date(p.text if p is not None else "")})
    return items


def from_wp_json(posts: list) -> list[dict]:
    out = []
    for p in posts or []:
        title = _clean(BeautifulSoup((p.get("title") or {}).get("rendered", ""), "lxml").get_text(" "))
        excerpt = _clean(BeautifulSoup((p.get("excerpt") or {}).get("rendered", ""), "lxml").get_text(" "))
        content = _clean(BeautifulSoup((p.get("content") or {}).get("rendered", ""), "lxml").get_text(" "))
        if title and p.get("link") and not NOT_A_JOB.search(title):
            out.append({"title": title[:260], "url": p["link"], "context": excerpt[:900],
                        "full_text": content, "published": (p.get("date") or "")[:10] or None})
    return out


def page_text(html: str) -> str:
    """Readable text of a detail page."""
    soup = BeautifulSoup(html, "lxml")
    for t in soup(["script", "style", "noscript", "nav", "header", "footer", "form", "svg", "aside"]):
        t.decompose()
    main = soup.find("main") or soup.find("article") or soup.body or soup
    return _clean(main.get_text(" ", strip=True))


def pdf_links(html: str, base_url: str) -> list[str]:
    soup = BeautifulSoup(html, "lxml")
    return [urljoin(base_url, a["href"]) for a in soup.find_all("a", href=True)
            if a["href"].lower().split("?")[0].endswith(".pdf")]


# ───────────────────────── deadline extraction ─────────────────────────

_MON = (r"(jan(?:uary)?|feb(?:ruary)?|mar(?:ch)?|apr(?:il)?|may|jun(?:e)?|jul(?:y)?|aug(?:ust)?|"
        r"sep(?:t(?:ember)?)?|oct(?:ober)?|nov(?:ember)?|dec(?:ember)?)")
MONTHS = {m: i for i, m in enumerate(
    ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"], 1)}

DATE_PATTERNS = [
    # 30 November 2026 / 30th Nov, 2026 / 30-Nov-2026
    (re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?[\s\-.,/]*(?:of\s+)?{_MON}\.?[\s\-.,/]*(\d{{4}})\b", re.I), "dmy_name"),
    # November 30, 2026
    (re.compile(rf"\b{_MON}\.?\s+(\d{{1,2}})(?:st|nd|rd|th)?,?\s+(\d{{4}})\b", re.I), "mdy_name"),
    # 2026-11-30
    (re.compile(r"\b(20\d\d)-(\d{1,2})-(\d{1,2})\b"), "ymd"),
    # 30/11/2026, 30.11.2026, 30-11-2026  (day first: India & Europe)
    (re.compile(r"\b(\d{1,2})[./-](\d{1,2})[./-](20\d\d)\b"), "dmy_num"),
    # "Closes 01 Nov" (no year — jobs.ac.uk style)
    (re.compile(rf"\b(\d{{1,2}})(?:st|nd|rd|th)?\s+{_MON}\b(?![\s\-.,/]*(?:of\s+)?\d)", re.I), "dm_noyear"),
]

CUE = re.compile(
    r"(last\s+date|closing\s+date|closes?\b|closing\b|deadline|apply\s+(?:by|before|latest\s+by|on\s+or\s+before)|"
    r"on\s+or\s+before|extended\s+(?:up\s?to|till|until)|up\s?to|till|until|due\s+date|last\s+day|"
    r"applications?\s+(?:will\s+be\s+)?(?:accepted|received|open)\s+(?:up\s?to|till|until)|"
    r"application\s+period\s+(?:ends|closes)|sista\s+ansökningsdag|bewerbungsschluss|reageren\s+tot)",
    re.I,
)


def _mk(y: int, m: int, d: int) -> dt.date | None:
    try:
        date = dt.date(y, m, d)
    except ValueError:
        return None
    return date if 2020 <= y <= 2035 else None


def _dates_in(s: str, today: dt.date) -> list[tuple[int, dt.date]]:
    found = []
    for rx, kind in DATE_PATTERNS:
        for m in rx.finditer(s):
            g = m.groups()
            date = None
            if kind == "dmy_name":
                date = _mk(int(g[2]), MONTHS[g[1][:3].lower()], int(g[0]))
            elif kind == "mdy_name":
                date = _mk(int(g[2]), MONTHS[g[0][:3].lower()], int(g[1]))
            elif kind == "ymd":
                date = _mk(int(g[0]), int(g[1]), int(g[2]))
            elif kind == "dmy_num":
                date = _mk(int(g[2]), int(g[1]), int(g[0]))
            elif kind == "dm_noyear":
                mo, d = MONTHS[g[1][:3].lower()], int(g[0])
                date = _mk(today.year, mo, d)
                if date and date < today - dt.timedelta(days=60):
                    date = _mk(today.year + 1, mo, d)
            if date:
                found.append((m.start(), date))
    return sorted(found)


def find_deadline(text: str, today: dt.date | None = None) -> str | None:
    """Return the application deadline (ISO) mentioned after a deadline cue, else None.
    When several cue-dates exist (e.g. 'last date extended'), the latest one wins."""
    if not text:
        return None
    today = today or dt.date.today()
    best = None
    for cue in CUE.finditer(text):
        window = text[cue.end(): cue.end() + 90]
        ds = _dates_in(window, today)
        if ds:
            d = ds[0][1]
            if best is None or d > best:
                best = d
    return best.isoformat() if best else None


def _parse_any_date(s: str) -> str | None:
    if not s:
        return None
    try:
        from dateutil import parser
        return parser.parse(s, fuzzy=True).date().isoformat()
    except Exception:
        return None


def domain(url: str) -> str:
    return urlparse(url).netloc.replace("www.", "")
