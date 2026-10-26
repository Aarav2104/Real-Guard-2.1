"""Real Guard: deterministic classification + policy evaluation + transformation."""
from time import perf_counter
from .classifier import classify
from .transforms import apply
from .validator import validate

FALLBACK = {"id": "FALLBACK-STRICT", "jurisdiction": "UNRESOLVED", "regulation": "Fallback strict policy (no validated jurisdiction policy available)",
            "source": "Internal default - not an official source", "version": "n/a", "effective_date": None, "origin": "builtin", "status": "active",
            "rules": [
                *({"field": f, "action": "ALLOW", "method": "pass", "ref": "fallback"} for f in ("like", "save", "follow", "share", "repost", "story_view", "skills", "job_interest")),
                *({"field": f, "action": "BLOCK", "method": "block", "ref": "fallback"} for f in ("email", "phone", "name", "account_id", "city", "education", "search", "resume", "comment", "caption", "dm", "geo", "profile_visit", "hashtag")),
                {"field": "device", "action": "TRANSFORM", "method": "device_family", "ref": "fallback"},
                {"field": "age", "action": "TRANSFORM", "method": "age_range", "param": 10, "ref": "fallback"},
                {"field": "watch_time", "action": "TRANSFORM", "method": "bucket", "param": 10, "ref": "fallback"}]}
assert validate(FALLBACK)["valid"]

def find_rule(policy, field, purpose):
    for r in policy["rules"]:
        if r["field"] == field and (not r.get("purposes") or purpose in r["purposes"]):
            return r
    return None

def evaluate(field, value, purpose, policy):
    t0 = perf_counter()
    cls, weight = classify(field, value)
    rule = find_rule(policy, field, purpose)
    missing = rule is None
    if missing: rule = {"field": field, "action": "BLOCK", "method": "block", "ref": "default-deny"}
    try: out, signal = apply(rule, value)
    except (ValueError, TypeError): out, signal = None, None
    action, method = rule["action"], rule["method"]
    if out is None and action != "BLOCK": action, method = "BLOCK", "block"
    return {"policy_id": policy["id"], "classification": cls, "weight": weight, "action": action, "method": method,
            "rule": "no matching rule -> default deny" if missing else f"{policy['id']}#{field}",
            "rule_ref": rule.get("ref"), "protected": out, "signal": signal,
            "latency_ms": (perf_counter() - t0) * 1000}
