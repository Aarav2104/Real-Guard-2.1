"""LLM-assisted structuring. Output is an UNTRUSTED candidate: it must pass validator.validate before activation."""
import json, re
from datetime import datetime, timezone
from . import db, llm
from .sources import SOURCES
from .validator import ACTIONS, METHODS
from .classifier import FIELD_CLASS

class StructuringError(Exception):
    def __init__(self, code, message): super().__init__(message); self.code = code

PROMPT = """You convert privacy regulation text into machine-readable rules for a social-media metadata guard.
Jurisdiction: {j} ({reg}).
Allowed fields: {fields}.
Allowed actions and the methods valid for each: {methods}. age_range and bucket need a numeric "param" (width).
Return ONLY a JSON object, no prose, with this shape:
{{"rules":[{{"field":"...","action":"...","method":"...","param":null,"ref":"the section/article of the text that supports this rule"}}]}}
Only emit a rule if the text supports it; cite it in "ref". Never ALLOW direct identifiers or sensitive data unmodified.
REGULATION TEXT:
{text}"""

def call_llm(prompt):
    """Isolated so tests can replace it. All provider details live in llm.py."""
    try: return llm.complete(prompt)
    except llm.LLMError as e: raise StructuringError(e.code, str(e))

def parse(raw):
    m = re.search(r"\{.*\}", raw, re.S)
    if not m: raise StructuringError("llm_bad_output", "no JSON object in LLM output")
    try: return json.loads(m.group(0))
    except json.JSONDecodeError as e: raise StructuringError("llm_bad_output", f"invalid JSON: {e}")

def structure(code):
    try: llm.require_configured()  # fail fast and loudly before any other work
    except llm.LLMError as e: raise StructuringError(e.code, str(e))
    entry = SOURCES.get(code)
    if not entry: raise StructuringError("no_source", f"no registered sources for {code}")
    src = db.q("SELECT * FROM sources WHERE jurisdiction=? AND status='ok' ORDER BY id DESC LIMIT 1", (code,))
    if not src: raise StructuringError("no_source_text", "run discovery first; no successfully fetched source text")
    s = src[0]
    prompt = PROMPT.format(j=code, reg=entry["regulation"], fields=", ".join(FIELD_CLASS),
                           methods=json.dumps({a: list(m) for a, m in METHODS.items()}), text=s["text"][:12000])
    data = parse(call_llm(prompt))
    return {"jurisdiction": code, "regulation": entry["regulation"], "source": f"{s['name']} - {s['url']}", "version": "LLM-structured candidate",
            "effective_date": None, "retrieved_at": s["fetched_at"], "source_sha256": s["sha256"], "rules": data.get("rules")}
