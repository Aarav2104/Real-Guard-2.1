"""Deterministic privacy transformations. Each returns (protected_value, numeric_signal)."""
import hashlib, hmac, re
from .config import PSEUDONYM_KEY

REGIONS = {"coimbatore": "Tamil Nadu", "chennai": "Tamil Nadu", "madurai": "Tamil Nadu", "mumbai": "Maharashtra",
           "pune": "Maharashtra", "delhi": "Delhi", "bengaluru": "Karnataka", "bangalore": "Karnataka",
           "hyderabad": "Telangana", "berlin": "Berlin (Germany)", "munich": "Bavaria (Germany)",
           "paris": "Île-de-France (France)", "madrid": "Madrid (Spain)", "austin": "Texas", "dallas": "Texas",
           "san francisco": "California", "los angeles": "California", "new york": "New York"}
KW = {"Photography": r"\b(photo\w*|camera|lens|film|shoot\w*)\b", "AI": r"\b(ai|ml|machine learning|artificial\w*)\b", "Tech": r"\b(tech|software|python|code|coding|engineer\w*|intern\w*|developer)\b",
      "Travel": r"\b(travel|trip|hike|hiking)\b", "Food": r"\b(food|cook\w*|recipe)\b", "Fitness": r"\b(fit\w*|gym|workout)\b",
      "Music": r"\b(music|guitar|song)\b", "Art": r"\b(art|design|paint\w*)\b", "Fashion": r"\b(fashion|style|outfit)\b"}
_KW = {k: re.compile(v, re.I) for k, v in KW.items()}

def category_of(text):
    return next((c for c, p in _KW.items() if p.search(str(text))), None)

DEVICES = [("iOS", re.compile(r"iphone|ipad|ios", re.I)), ("Android", re.compile(r"android", re.I)), ("Windows", re.compile(r"windows", re.I)),
           ("macOS", re.compile(r"macintosh|mac os", re.I)), ("Linux", re.compile(r"linux|x11", re.I))]

def _band(value, width):
    lo = int(float(value) // width * width)
    return lo, lo + int(width)

def apply(rule, value):
    m, p = rule["method"], rule.get("param")
    if m == "pass": return str(value), None
    if m == "redact": return "[REDACTED]", None
    if m == "block": return None, None
    if m == "pseudonym":
        return "tok_" + hmac.new(PSEUDONYM_KEY.encode(), str(value).encode(), hashlib.sha256).hexdigest()[:10], None
    if m == "age_range":
        lo, hi = _band(value, p); return f"{lo}–{hi}", None
    if m == "bucket":
        lo, hi = _band(value, p); return f"{lo}–{hi} s", lo + p / 2
    if m == "device_family": return next((n for n, p in DEVICES if p.search(str(value))), "Other device"), None
    if m == "precision":
        lat, lng = (float(v) for v in str(value).split(","))
        return f"{lat:.{int(p)}f},{lng:.{int(p)}f}", None
    if m == "region": return REGIONS.get(str(value).strip().lower(), "Unspecified region"), None
    if m == "category": return category_of(value) or "[no category match]", None
    raise ValueError(f"unknown method {m}")
