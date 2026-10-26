from app import guard, jurisdiction, reference_policies as ref
from app.validator import validate

IN = ref.REFERENCE[0]

def ev(f, v, pol=None, purpose="recommendation"):
    return guard.evaluate(f, v, purpose, {**(pol or IN), "id": "T"})

def test_reference_policies_valid():
    assert all(validate(p, p["jurisdiction"])["valid"] for p in ref.REFERENCE)

def test_transformations():
    assert ev("age", 21)["protected"] == "20–25"
    assert ev("email", "a@b.co")["protected"] == "[REDACTED]" and ev("email", "a@b.co")["action"] == "REDACT"
    assert ev("watch_time", 18)["protected"] == "15–20 s" and ev("watch_time", 18)["signal"] == 17.5
    assert ev("city", "Coimbatore")["protected"] == "Tamil Nadu"
    assert ev("resume", "cv.pdf")["action"] == "BLOCK"
    assert ev("like", "p1")["action"] == "ALLOW"

def test_pseudonym_deterministic():
    assert ev("name", "Aarav")["protected"] == ev("name", "Aarav")["protected"] != ev("name", "Bob")["protected"]

def test_unknown_field_default_deny_and_bad_value_blocks():
    assert ev("blood_type", "O+")["action"] == "BLOCK"
    assert ev("age", "not-a-number")["action"] == "BLOCK"

def test_fallback_is_strict():
    d = guard.evaluate("email", "a@b.co", "recommendation", guard.FALLBACK)
    assert d["action"] == "BLOCK" and guard.evaluate("city", "Pune", "x", guard.FALLBACK)["action"] == "BLOCK"

def test_purpose_constraint():
    pol = {"id": "P", "rules": [{"field": "age", "action": "BLOCK", "method": "block", "ref": "r", "purposes": ["ads"]},
                                {"field": "age", "action": "TRANSFORM", "method": "age_range", "param": 5, "ref": "r", "purposes": ["recommendation"]}]}
    assert guard.evaluate("age", 21, "ads", pol)["action"] == "BLOCK"
    assert guard.evaluate("age", 21, "recommendation", pol)["protected"] == "20–25"
    assert guard.evaluate("age", 21, "other", pol)["action"] == "BLOCK"  # no matching rule -> default deny

def test_validator_rejects_bad_policies():
    bad = {"jurisdiction": "IN", "regulation": "x", "source": "s", "version": "1", "rules": [
        {"field": "email", "action": "ALLOW", "method": "pass", "ref": "r"},
        {"field": "dna", "action": "ALLOW", "method": "pass", "ref": "r"},
        {"field": "age", "action": "TRANSFORM", "method": "age_range", "param": 0, "ref": "r"},
        {"field": "age", "action": "BLOCK", "method": "block", "ref": "r"},
        {"field": "like", "action": "REDACT", "method": "pass", "ref": ""}]}
    v = validate(bad, "IN"); text = " ".join(v["errors"])
    assert not v["valid"] and all(k in text for k in ("unsafe", "unsupported", "positive", "conflicts", "not valid for REDACT", "missing policy reference"))
    assert not validate({**bad, "rules": []}, "EU")["valid"]

def test_jurisdiction_detection():
    assert jurisdiction.detect("Asia/Kolkata", "en-US")["code"] == "IN"
    assert jurisdiction.detect("Europe/Berlin", None)["code"] == "EU"
    assert jurisdiction.detect("Europe/London", "en-GB")["code"] == "UNKNOWN"
    assert jurisdiction.detect("Asia/Kolkata", None, "BR")["code"] == "BR"
    assert not jurisdiction.detect(None, None)["resolved"]

def test_new_metadata_types():
    assert ev("dm", "meet me at 5, my number is 99999")["action"] == "BLOCK"
    c = ev("comment", "great lens and camera work")
    assert c["action"] == "TRANSFORM" and c["protected"] == "Photography"
    assert ev("device", "Mozilla/5.0 (iPhone; CPU iPhone OS 17 like Mac OS X)")["protected"] == "iOS"
    assert ev("device", "Mozilla/5.0 (Windows NT 10.0; Win64)")["protected"] == "Windows"
    assert ev("geo", "11.0168,76.9558")["protected"] == "11.0,77.0"
    assert ev("profile_visit", "lens.stories")["protected"].startswith("tok_")
    assert guard.evaluate("geo", "11.0168,76.9558", "x", guard.FALLBACK)["action"] == "BLOCK"
    assert guard.evaluate("geo", "bad", "recommendation", {**IN, "id": "T"})["action"] == "BLOCK"
