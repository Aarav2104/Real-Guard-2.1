"""Real Guard API + static frontend. Run: uvicorn app.main:app --reload  (from backend/)"""
import json, uuid
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from . import catalog, db, discovery, guard, llm, metrics, recommender, repository, structuring
from .config import FRONTEND
from .jurisdiction import detect
from .sources import SOURCES
from .validator import validate

@asynccontextmanager
async def lifespan(_):
    db.conn(); repository.seed()
    st = llm.status(); print(f"[Real Guard] LLM provider={st.get('provider')} model={st.get('model')} key={'set' if st.get('configured') else 'MISSING (policy structuring disabled; guard still works)'}")
    yield

app = FastAPI(title="Real Guard", version="1.0", lifespan=lifespan)

class SessionIn(BaseModel):
    tz: Optional[str] = None
    lang: Optional[str] = None
    region_override: Optional[str] = None

class EventIn(BaseModel):
    session_id: str
    field: str
    value: Any
    source: str = "app"
    purpose: str = "recommendation"
    ad_id: Optional[str] = None
    category: Optional[str] = None

class BatchIn(BaseModel):
    session_id: str
    items: list[dict]
    source: str
    purpose: str
    ad_id: str
    category: Optional[str] = None

class RegionIn(BaseModel):
    region: str

class ValidateIn(BaseModel):
    policy: Any
    jurisdiction: Optional[str] = None

def _session(sid):
    r = db.q("SELECT * FROM sessions WHERE id=?", (sid,))
    if not r: raise HTTPException(404, "unknown session")
    return r[0]

def _policy_for(code):
    return repository.get_active(code) or guard.FALLBACK

def _store(s, field, value, source, purpose, ad_id, cat, ev_id=None):
    pol = _policy_for(s["jurisdiction"]); d = guard.evaluate(field, value, purpose, pol)
    if ev_id:
        db.x("UPDATE events SET jurisdiction=?,policy_id=?,classification=?,weight=?,action=?,method=?,rule=?,rule_ref=?,protected=?,signal=?,latency_ms=? WHERE id=?",
             (s["jurisdiction"], d["policy_id"], d["classification"], d["weight"], d["action"], d["method"], d["rule"], d["rule_ref"], d["protected"], d["signal"], d["latency_ms"], ev_id))
        return d
    eid = db.x("INSERT INTO events(session_id,field,original,source,purpose,ad_id,ctx_cat,ts,jurisdiction,policy_id,classification,weight,action,method,rule,rule_ref,protected,signal,latency_ms) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
               (s["id"], field, str(value), source, purpose, ad_id, cat, datetime.now().strftime("%H:%M:%S"), s["jurisdiction"], d["policy_id"], d["classification"], d["weight"],
                d["action"], d["method"], d["rule"], d["rule_ref"], d["protected"], d["signal"], d["latency_ms"]))
    return {"id": eid, "field": field, **{k: d[k] for k in ("action", "method", "classification", "protected", "rule", "policy_id")}}

def _reprocess(s):
    for e in db.q("SELECT * FROM events WHERE session_id=?", (s["id"],)):
        _store(s, e["field"], e["original"], e["source"], e["purpose"], e["ad_id"], e["ctx_cat"], ev_id=e["id"])

@app.get("/api/health")
def health(): return {"ok": True, "llm_configured": llm.status()["configured"]}

@app.get("/api/llm/status")
def llm_status(): return llm.status()

@app.get("/api/catalog")
def get_catalog(): return {"posts": catalog.POSTS, "ad": catalog.AD, "categories": catalog.CATS}

@app.post("/api/session")
def new_session(b: SessionIn):
    j = detect(b.tz, b.lang, b.region_override); sid = uuid.uuid4().hex
    db.x("INSERT INTO sessions VALUES(?,?,?,?,?,?,?)", (sid, b.tz, b.lang, b.region_override, j["code"], j["source"], datetime.now(timezone.utc).isoformat()))
    return {"session_id": sid, "jurisdiction": j}

@app.get("/api/session/{sid}")
def get_session(sid: str):
    s = _session(sid); pol = _policy_for(s["jurisdiction"])
    j = detect(s["tz"], s["lang"], s["region_override"])
    return {"session_id": sid, "jurisdiction": j, "policy": {k: pol.get(k) for k in ("id", "jurisdiction", "regulation", "source", "version", "effective_date", "retrieved_at", "origin", "rules")},
            "policy_validation": pol.get("validation", {"valid": True, "errors": [], "warnings": []}), "fallback": pol["id"] == guard.FALLBACK["id"],
            "registered_sources": [x["url"] for x in SOURCES.get(s["jurisdiction"], {}).get("sources", [])]}

@app.post("/api/session/{sid}/region")
def set_region(sid: str, b: RegionIn):
    s = _session(sid); j = detect(s["tz"], s["lang"], b.region)
    db.x("UPDATE sessions SET region_override=?,jurisdiction=?,jurisdiction_source=? WHERE id=?", (b.region, j["code"], j["source"], sid))
    s = _session(sid); _reprocess(s)
    return get_session(sid)

@app.post("/api/session/{sid}/reprocess")
def reprocess(sid: str):
    _reprocess(_session(sid)); return {"ok": True}

@app.post("/api/session/{sid}/reset")
def reset(sid: str):
    _session(sid); db.x("DELETE FROM events WHERE session_id=?", (sid,)); return {"ok": True}

@app.post("/api/events")
def post_event(b: EventIn):
    return _store(_session(b.session_id), b.field, b.value, b.source, b.purpose, b.ad_id, b.category)

@app.post("/api/events/batch")
def post_batch(b: BatchIn):
    s = _session(b.session_id)
    if not b.items: raise HTTPException(422, "no fields submitted")
    out = [_store(s, i["field"], i["value"], b.source, b.purpose, b.ad_id, b.category) for i in b.items if "field" in i and i.get("value") not in (None, "")]
    return {"ad_id": b.ad_id, "decisions": out}

@app.get("/api/events")
def list_events(session_id: str):
    _session(session_id)  # NOTE: returns originals for the analysis view only (synthetic data); recommender never sees them
    return db.q("SELECT * FROM events WHERE session_id=? ORDER BY id", (session_id,))

@app.get("/api/ads")
def ads(session_id: str):
    rows = [e for e in db.q("SELECT * FROM events WHERE session_id=? AND ad_id IS NOT NULL ORDER BY id", (session_id,))]
    return rows

@app.get("/api/metrics")
def get_metrics(session_id: str):
    _session(session_id); return metrics.compute(db.q("SELECT * FROM events WHERE session_id=?", (session_id,)))

@app.get("/api/recommendations")
def recs(session_id: str):
    rows = db.q("SELECT * FROM events WHERE session_id=?", (session_id,))
    prof = recommender.profile(rows, protected=True)  # protected values only
    return {"profile": prof, "items": recommender.top_k(prof)}

@app.get("/api/policies")
def policies(jurisdiction: Optional[str] = None):
    return [{k: p[k] for k in ("id", "jurisdiction", "regulation", "origin", "status", "version", "validation", "created_at")} for p in repository.list_policies(jurisdiction)]

@app.post("/api/policies/validate")
def validate_policy(b: ValidateIn): return validate(b.policy, b.jurisdiction)

@app.get("/api/policies/{code}/sources")
def source_log(code: str):
    return db.q("SELECT id,jurisdiction,name,url,fetched_at,status,http_status,sha256,error FROM sources WHERE jurisdiction=? ORDER BY id DESC LIMIT 20", (code,))

@app.post("/api/policies/{code}/discover")
def discover(code: str): return {"results": discovery.discover(code)}

@app.post("/api/policies/{code}/structure")
def structure(code: str):
    try: candidate = structuring.structure(code)
    except structuring.StructuringError as e:
        return {"ok": False, "stage": "structuring", "code": e.code, "message": str(e)}
    p = repository.add(candidate, "llm")
    return {"ok": p["validation"]["valid"], "stage": "validation", "policy_id": p["id"], "status": p["status"], "validation": p["validation"]}

@app.post("/api/policies/{pid}/activate")
def activate(pid: str):
    try: p = repository.activate(pid)
    except KeyError: raise HTTPException(404, "policy not found")
    except ValueError as e: raise HTTPException(422, str(e))
    return {"ok": True, "policy_id": p["id"], "status": p["status"]}

@app.get("/api/selftest")
def selftest():
    """Transformation correctness against the IN reference policy."""
    pol = repository.get_active("IN") or guard.FALLBACK
    cases = [("age", 21, "20–25"), ("email", "user@example.com", "[REDACTED]"), ("watch_time", 18, "15–20 s"), ("city", "Coimbatore", "Tamil Nadu"), ("resume", "cv.pdf", None), ("like", "p1", "p1")]
    res = [{"field": f, "input": v, "expected": e, "got": (g := guard.evaluate(f, v, "recommendation", pol))["protected"], "pass": g["protected"] == e} for f, v, e in cases]
    return {"policy": pol["id"], "passed": sum(r["pass"] for r in res), "total": len(res), "cases": res}

app.mount("/", StaticFiles(directory=str(FRONTEND), html=True), name="ui")
