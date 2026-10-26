"""Policy validation gate. Nothing becomes active unless this returns valid=True."""
from .classifier import FIELD_CLASS

ACTIONS = ("ALLOW", "TRANSFORM", "REDACT", "BLOCK")
METHODS = {"ALLOW": ("pass",), "REDACT": ("redact",), "BLOCK": ("block",),
           "TRANSFORM": ("pseudonym", "age_range", "region", "bucket", "category", "device_family", "precision")}
REQUIRED = ("jurisdiction", "regulation", "source", "version", "rules")
UNSAFE_ALLOW = ("DIRECT_IDENTIFIER", "SENSITIVE_DATA")

def validate(policy, expected_jurisdiction=None):
    errors, warnings = [], []
    if not isinstance(policy, dict):
        return {"valid": False, "errors": ["policy must be a JSON object"], "warnings": []}
    for k in REQUIRED:
        if not policy.get(k): errors.append(f"missing required field: {k}")
    if expected_jurisdiction and policy.get("jurisdiction") not in (None, expected_jurisdiction):
        errors.append(f"jurisdiction mismatch: policy says {policy.get('jurisdiction')!r}, expected {expected_jurisdiction!r}")
    rules = policy.get("rules") if isinstance(policy.get("rules"), list) else []
    seen = {}
    for i, r in enumerate(rules):
        if not isinstance(r, dict): errors.append(f"rule {i}: not an object"); continue
        f, a, m, p = r.get("field"), r.get("action"), r.get("method"), r.get("param")
        if f not in FIELD_CLASS: errors.append(f"rule {i}: unsupported data field {f!r}")
        if a not in ACTIONS: errors.append(f"rule {i}: invalid action {a!r}")
        elif m not in METHODS[a]: errors.append(f"rule {i}: method {m!r} not valid for {a}")
        if m in ("age_range", "bucket") and not (isinstance(p, (int, float)) and not isinstance(p, bool) and p > 0):
            errors.append(f"rule {i}: method {m} needs a positive numeric param")
        if m == "precision" and not (isinstance(p, int) and not isinstance(p, bool) and p >= 0):
            errors.append(f"rule {i}: precision needs a non-negative integer param")
        if not str(r.get("ref") or "").strip(): errors.append(f"rule {i}: missing policy reference (ref)")
        purposes = r.get("purposes")
        if purposes is not None and not (isinstance(purposes, list) and purposes and all(isinstance(x, str) for x in purposes)):
            errors.append(f"rule {i}: purposes must be a non-empty list of strings")
        if a == "ALLOW" and FIELD_CLASS.get(f) in UNSAFE_ALLOW:
            errors.append(f"rule {i}: ALLOW for {FIELD_CLASS[f]} field {f!r} is ambiguous/unsafe; use TRANSFORM, REDACT or BLOCK")
        for j, prev in seen.get(f, []):
            pa, pb = set(prev.get("purposes") or []), set(purposes or [])
            if not pa or not pb or pa & pb:
                errors.append(f"rule {i}: conflicts with rule {j} for field {f!r} (overlapping purposes)")
        seen.setdefault(f, []).append((i, r))
    for f in FIELD_CLASS:
        if f not in seen: warnings.append(f"no rule for {f!r}: runtime default is BLOCK")
    return {"valid": not errors, "errors": errors, "warnings": warnings}
