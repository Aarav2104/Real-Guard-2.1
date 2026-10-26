"""Policy discovery: fetch registry sources, keep traceable raw text. Never raises; failures are recorded."""
import hashlib, re
from datetime import datetime, timezone
from html.parser import HTMLParser
import httpx
from . import db
from .config import HTTP_TIMEOUT
from .sources import SOURCES

class _Text(HTMLParser):
    def __init__(self): super().__init__(); self.parts = []; self.skip = 0
    def handle_starttag(self, t, a): self.skip += t in ("script", "style")
    def handle_endtag(self, t): self.skip -= t in ("script", "style")
    def handle_data(self, d):
        if self.skip <= 0 and d.strip(): self.parts.append(d.strip())

def html_to_text(html):
    p = _Text(); p.feed(html); return re.sub(r"\s+", " ", " ".join(p.parts))

def fetch(url):
    """Isolated so tests can replace it. Returns (http_status, content_type, body_text)."""
    r = httpx.get(url, timeout=HTTP_TIMEOUT, follow_redirects=True, headers={"User-Agent": "RealGuard-research-prototype/1.0"})
    return r.status_code, r.headers.get("content-type", ""), r.text

def discover(code):
    entry = SOURCES.get(code)
    if not entry: return [{"status": "no_registered_source", "error": f"no authoritative source registered for {code}"}]
    results = []
    for s in entry["sources"]:
        now = datetime.now(timezone.utc).isoformat(timespec="seconds")
        row = {"jurisdiction": code, "name": s["name"], "url": s["url"], "fetched_at": now, "status": "ok", "http_status": None, "sha256": None, "text": None, "error": None}
        try:
            code_, ctype, body = fetch(s["url"])
            row["http_status"] = code_
            if code_ != 200: row.update(status="http_error", error=f"HTTP {code_}")
            elif "html" not in ctype.lower() and "text" not in ctype.lower(): row.update(status="unsupported_content_type", error=ctype)
            else:
                text = html_to_text(body)[:200000]
                row.update(text=text, sha256=hashlib.sha256(text.encode()).hexdigest())
                if len(text) < 200: row.update(status="empty_content", error="page text too short to structure")
        except Exception as e:  # network errors must not break the pipeline
            row.update(status="fetch_failed", error=f"{type(e).__name__}: {e}"[:300])
        db.x("INSERT INTO sources(jurisdiction,name,url,fetched_at,status,http_status,sha256,text,error) VALUES(?,?,?,?,?,?,?,?,?)",
             (code, row["name"], row["url"], now, row["status"], row["http_status"], row["sha256"], row["text"], row["error"]))
        results.append({k: v for k, v in row.items() if k != "text"} | {"chars": len(row["text"] or "")})
    return results
