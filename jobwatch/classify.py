"""Rule-based classification: category, region/country and relevance score.
Fast, free and deterministic; the optional AI step refines these numbers."""
from __future__ import annotations

import re

R = lambda p: re.compile(p, re.I)  # noqa: E731

PHD = R(r"\bph\.?\s?d\.?\s*(student|position|scholarship|fellowship|candidate|program|studentship|opportunit)|"
        r"doctoral (student|candidate|researcher position)|predoctoral|pre-doctoral|doktorand|"
        r"\bdoctoral (position|scholarship)|studentship|master'?s? (student|thesis)|internship")
PROJECT = R(r"project (scientist|associate|assistant|staff|research|manager|technical|coordinator)|"
            r"\bjrf\b|\bsrf\b|junior research fellow|senior research fellow|young professional|"
            r"field (worker|investigator)|technical assistant|lab(oratory)? (assistant|technician)|"
            r"research assistant|data entry|technician|consultant|research engineer")
POSTDOC = R(r"post-?doc|post[\s-]?doctoral|research associate|\bRA[\s-]?(i{1,3}|[123])\b|\bn-?pdf\b|"
            r"research fellow\b|postdoktor|university assistant\s*\(?post-?doc|"
            r"early[\s-]career (researcher|fellow)")
NAMED_FELLOWSHIP = R(r"ramalingaswami|inspire faculty|ramanujan fellow|india alliance|wellcome|embo|"
                     r"marie (skłodowska|sklodowska|curie)|\bmsca\b|humboldt|hfsp|jsps|newton international|"
                     r"eipod|pulse postdoc|excellence scholarship|fulbright")
PERMANENT = R(r"scientist[\s\-–]*['‘’\"]?\s*(?:[b-g]|i{1,3}|iv|v|vi|[1-6])\b['’\"]?|"
              r"assistant professor|associate professor|\bprofessor\b|faculty|lecturer|tenure[\s-]?track|"
              r"group leader|staff scientist|principal investigator|senior scientist|scientific officer|"
              r"research scientist|\bscientists?\b|investigator\b|chair (of|in)\b|reader in")
FELLOWSHIP = R(r"fellowship|\bfellow\b")
CONTRACT = R(r"contract(ual)?\b|deputation|ad[\s-]?hoc|guest faculty|visiting faculty|temporary|"
             r"outsourc|manpower agency|fixed[\s-]term|\bon tenure basis")

INDIA = R(r"\bindia\b|\bindian\b|\biit\b|\biiser\b|\bnit\b|\baiims\b|\bcsir\b|\bicmr\b|\bdbt\b|\bdst\b|"
          r"\bicar\b|\bbric\b|\biisc\b|\bncbs\b|\bjnu\b|\bbhu\b|\bjncasr\b|\bniser\b|\biacs\b|\btifr\b|"
          r"delhi|mumbai|bengaluru|bangalore|hyderabad|chennai|kolkata|pune|bhubaneswar|lucknow|"
          r"chandigarh|mohali|kerala|tamil nadu|karnataka|maharashtra|gujarat|odisha|assam|"
          r"uttar pradesh|\bup\b,? india|west bengal|telangana|punjab|haryana|rajasthan|bihar|"
          r"madhya pradesh|thiruvananthapuram|kalyani|faridabad|gandhinagar|indore|bhopal|kanpur")

COUNTRIES = [
    "Sweden", "Netherlands", "Switzerland", "Germany", "Singapore", "Australia", "Denmark", "Austria",
    "United Kingdom", "UK", "England", "Scotland", "Ireland", "France", "Spain", "Italy", "Belgium",
    "Norway", "Finland", "Portugal", "Czech Republic", "Poland", "Israel", "Japan", "South Korea", "Korea",
    "China", "Hong Kong", "Taiwan", "Canada", "United States", "USA", "New Zealand", "Luxembourg",
    "Estonia", "Iceland", "Saudi Arabia", "Qatar", "United Arab Emirates", "UAE",
]
COUNTRY_RX = R(r"\b(" + "|".join(re.escape(c) for c in COUNTRIES) + r")\b")
COUNTRY_NORMALISE = {"uk": "United Kingdom", "england": "United Kingdom", "scotland": "United Kingdom",
                     "usa": "United States", "korea": "South Korea", "uae": "United Arab Emirates"}


def categorise(title: str, context: str = "", default: str | None = None) -> str:
    t = title or ""
    tc = f"{t} {context or ''}"
    if PHD.search(t) and not POSTDOC.search(t):
        return "phd"
    if PROJECT.search(t) and not PERMANENT.search(re.sub(PROJECT, "", t)):
        return "project"
    if POSTDOC.search(t):
        return "postdoc"
    if NAMED_FELLOWSHIP.search(t):
        return "fellowship"
    if PERMANENT.search(t):
        return "permanent"
    if FELLOWSHIP.search(t):
        return "postdoc"
    # fall back to context (listing rows often say "Permanent Posts", "Postdoc" etc.)
    if re.search(r"permanent post|regular (post|position|faculty)|direct recruitment", tc, re.I):
        return "permanent"
    if POSTDOC.search(tc):
        return "postdoc"
    if PROJECT.search(tc):
        return "project"
    if PERMANENT.search(tc):
        return "permanent"
    return default or "other"


def is_contract(title: str) -> bool:
    return bool(CONTRACT.search(title or ""))


def region_country(text: str, source: dict) -> tuple[str, str]:
    reg = source.get("region", "mixed")
    if reg == "india":
        return "india", "India"
    m = COUNTRY_RX.search(text or "")
    if reg == "abroad":
        if m:
            c = m.group(1)
            return "abroad", COUNTRY_NORMALISE.get(c.lower(), c)
        return "abroad", source.get("country") or ""
    # mixed sources (aggregators)
    im = INDIA.search(text or "")
    if im and (not m or im.start() <= m.start()):
        return "india", "India"
    if m:
        c = m.group(1)
        return "abroad", COUNTRY_NORMALISE.get(c.lower(), c)
    return "abroad", ""


def _hits(words: list[str], text: str) -> list[str]:
    t = (text or "").lower()
    hits = [w.lower() for w in words if re.search(r"(?<![a-z])" + re.escape(w.lower()), t)]
    # "genomic" + "genomics" is one concept, not two
    return [h for h in hits if not any(h != o and h in o for o in hits)]


def score(item: dict, profile: dict, source: dict) -> dict:
    """Return {'score', 'matched', 'check_advt'} for an item using the profile keywords."""
    title = item.get("title", "")
    body = " ".join(filter(None, [item.get("context", ""), item.get("details", "")]))
    core_t = _hits(profile["core_keywords"], title)
    core_b = [w for w in _hits(profile["core_keywords"], body) if w not in core_t]
    all_t = _hits(profile["allied_keywords"], title)
    all_b = [w for w in _hits(profile["allied_keywords"], body) if w not in all_t]
    neg_t = _hits(profile["negative_keywords"], title)
    neg_b = _hits(profile["negative_keywords"], body)

    s = 0
    s += min(60, 30 * len(core_t)) + min(45, 15 * len(core_b))
    s += min(20, 10 * len(all_t)) + min(12, 4 * len(all_b))
    if source.get("topic_filtered"):
        s += 25
    check_advt = False
    cat = item.get("category")
    if cat in ("permanent", "postdoc", "fellowship"):
        s += 10                     # right career stage
    if source.get("life_science") and cat in ("permanent", "fellowship") and not (core_t or core_b):
        # e.g. "Advertisement for 30 vacancies of Scientist-B at ICMR" — subject list is inside the PDF
        s += 30
        check_advt = True
    if neg_t:
        s -= 60
    if neg_b and not (core_t or core_b):
        s -= min(30, 15 * len(neg_b))
    if cat in ("phd", "other"):
        s -= 15
    s = max(0, min(100, s))
    return {"score": s, "matched": sorted(set(core_t + core_b + all_t))[:8], "check_advt": check_advt}
