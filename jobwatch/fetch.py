"""HTTP fetching: polite session with retries, PDF support and optional headless rendering."""
from __future__ import annotations

import io
import logging
import threading
import time
from dataclasses import dataclass
from urllib.parse import urlparse

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

log = logging.getLogger(__name__)

UA = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0 Safari/537.36 JobWatch/1.0 (+https://github.com)"
)

_session: requests.Session | None = None
_last_hit: dict[str, float] = {}
_lock = threading.Lock()
PER_HOST_DELAY = 1.0  # seconds between requests to the same host


@dataclass
class Page:
    url: str          # final URL after redirects
    status: int
    content_type: str
    text: str         # HTML/XML text, or extracted PDF text
    is_pdf: bool = False


def session() -> requests.Session:
    global _session
    if _session is None:
        s = requests.Session()
        retry = Retry(total=2, backoff_factor=1.5, status_forcelist=(429, 500, 502, 503, 504),
                      allowed_methods=("GET", "POST"))
        s.mount("https://", HTTPAdapter(max_retries=retry))
        s.mount("http://", HTTPAdapter(max_retries=retry))
        s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"})
        _session = s
    return _session


def _throttle(url: str) -> None:
    """Reserve the next polite slot for this host (thread-safe), then wait for it."""
    host = urlparse(url).netloc
    with _lock:
        now = time.time()
        slot = max(now, _last_hit.get(host, 0) + PER_HOST_DELAY)
        _last_hit[host] = slot
    if slot > now:
        time.sleep(slot - now)


def pdf_to_text(data: bytes, max_pages: int = 6) -> str:
    try:
        from pypdf import PdfReader
        reader = PdfReader(io.BytesIO(data))
        return "\n".join((p.extract_text() or "") for p in reader.pages[:max_pages])
    except Exception as e:  # scanned / broken PDFs are common on govt sites
        log.debug("PDF parse failed: %s", e)
        return ""


def get(url: str, timeout: int = 25, render: bool = False) -> Page:
    """Fetch a URL. PDFs are converted to text. `render` uses Playwright if installed."""
    if render:
        page = _render(url, timeout)
        if page is not None:
            return page
    _throttle(url)
    r = session().get(url, timeout=timeout, allow_redirects=True)
    ctype = r.headers.get("content-type", "").lower()
    is_pdf = "pdf" in ctype or r.url.lower().split("?")[0].endswith(".pdf")
    if is_pdf:
        return Page(r.url, r.status_code, ctype, pdf_to_text(r.content), True)
    if not r.encoding or r.encoding.lower() == "iso-8859-1":
        r.encoding = r.apparent_encoding
    return Page(r.url, r.status_code, ctype, r.text, False)


def get_json(url: str, timeout: int = 30):
    _throttle(url)
    r = session().get(url, timeout=timeout, headers={"Accept": "application/json"})
    r.raise_for_status()
    return r.json()


_browser = None
_pw = None


def _render(url: str, timeout: int) -> Page | None:
    """Render JS-heavy pages with Playwright (optional dependency)."""
    global _browser, _pw
    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        log.info("Playwright not installed; fetching %s without rendering", url)
        return None
    try:
        if _browser is None:
            _pw = sync_playwright().start()
            _browser = _pw.chromium.launch()
        ctx = _browser.new_context(user_agent=UA)
        pg = ctx.new_page()
        resp = pg.goto(url, timeout=timeout * 1000, wait_until="networkidle")
        pg.wait_for_timeout(1500)
        html = pg.content()
        status = resp.status if resp else 200
        final = pg.url
        ctx.close()
        return Page(final, status, "text/html", html, False)
    except Exception as e:
        log.warning("Render failed for %s: %s", url, e)
        return None


def close() -> None:
    global _browser, _pw
    if _browser is not None:
        try:
            _browser.close()
            _pw.stop()
        except Exception:
            pass
        _browser = _pw = None
