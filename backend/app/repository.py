"""Policy repository: versioned storage; only validated policies can become active."""
import json, time
from datetime import datetime, timezone
from . import db
from .reference_policies import REFERENCE
from .validator import validate

def _row(r):
    r = dict(r); r["validation"] = json.loads(r["validation"]); r["body"] = json.loads(r["body"]); return r

def add(policy, origin):
    v = validate(policy, policy.get("jurisdiction"))
    pid = f"{policy.get('jurisdiction', 'X')}:{origin}:{time.time_ns()}"
    status = "valid_candidate" if v["valid"] else "rejected"
    db.x("INSERT INTO policies VALUES(?,?,?,?,?,?,?,?,?,?,?,?)", (pid, policy.get("jurisdiction"), policy.get("regulation"), policy.get("source"),
         policy.get("version"), policy.get("effective_date"), policy.get("retrieved_at"), origin, status, db.dumps(v), db.dumps(policy),
         datetime.now(timezone.utc).isoformat(timespec="seconds")))
    return get(pid)

def get(pid):
    r = db.q("SELECT * FROM policies WHERE id=?", (pid,)); return _row(r[0]) if r else None

def list_policies(j=None):
    rows = db.q("SELECT * FROM policies WHERE (?1 IS NULL OR jurisdiction=?1) ORDER BY created_at DESC, id DESC", (j,))
    return [_row(r) for r in rows]

def get_active(j):
    r = db.q("SELECT * FROM policies WHERE jurisdiction=? AND status='active' ORDER BY created_at DESC LIMIT 1", (j,))
    if not r: return None
    r = _row(r[0]); return {**r["body"], "id": r["id"], "origin": r["origin"], "status": r["status"], "validation": r["validation"]}

def activate(pid):
    p = get(pid)
    if not p: raise KeyError("policy not found")
    if not p["validation"]["valid"]: raise ValueError("policy failed validation and cannot be activated")
    db.x("UPDATE policies SET status='superseded' WHERE jurisdiction=? AND status='active'", (p["jurisdiction"],))
    db.x("UPDATE policies SET status='active' WHERE id=?", (pid,))
    return get(pid)

def seed():
    for pol in REFERENCE:
        if not get_active(pol["jurisdiction"]) and not db.q("SELECT 1 FROM policies WHERE jurisdiction=? AND origin='reference'", (pol["jurisdiction"],)):
            p = add(pol, "reference")
            if p["validation"]["valid"]: activate(p["id"])
