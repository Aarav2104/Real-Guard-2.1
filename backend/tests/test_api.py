from app import discovery, structuring

def test_selftest(client):
    r = client.get("/api/selftest").json(); assert r["passed"] == r["total"]

def test_events_and_metrics(client, sid):
    for f, v in [("age", 21), ("email", "demo@example.com"), ("city", "Coimbatore")]:
        assert client.post("/api/events", json={"session_id": sid, "field": f, "value": v, "category": None}).status_code == 200
    for _ in range(3):
        client.post("/api/events", json={"session_id": sid, "field": "like", "value": "p0", "category": "AI"})
    client.post("/api/events", json={"session_id": sid, "field": "watch_time", "value": 18, "category": "AI"})
    m = client.get("/api/metrics", params={"session_id": sid}).json()
    assert m["records"] == 7 and m["risk_after"] < m["risk_before"] and 0 < m["risk_reduction_pct"] < 100
    assert m["utility_retained_pct"] == 100.0
    assert client.get("/api/recommendations", params={"session_id": sid}).json()["items"][0]["cat"] == "AI"

def test_ad_batch(client, sid):
    items = [{"field": "name", "value": "Aarav"}, {"field": "email", "value": "a@b.co"}, {"field": "resume", "value": "cv.pdf"}, {"field": "skills", "value": "python, machine learning"}]
    r = client.post("/api/events/batch", json={"session_id": sid, "items": items, "source": "ad:nimbus", "purpose": "job_application", "ad_id": "ad1"}).json()
    assert [d["action"] for d in r["decisions"]] == ["TRANSFORM", "REDACT", "BLOCK", "ALLOW"]
    assert len(client.get("/api/ads", params={"session_id": sid}).json()) == 4

def test_unknown_jurisdiction_uses_fallback_and_reprocess(client, sid):
    client.post("/api/events", json={"session_id": sid, "field": "city", "value": "Pune"})
    s = client.post(f"/api/session/{sid}/region", json={"region": "BR"}).json()
    assert s["fallback"] and s["jurisdiction"]["code"] == "BR"
    assert client.get("/api/events", params={"session_id": sid}).json()[0]["action"] == "BLOCK"
    client.post(f"/api/session/{sid}/region", json={"region": "IN"})
    assert client.get("/api/events", params={"session_id": sid}).json()[0]["protected"] == "Maharashtra"

def test_unknown_session_and_empty_form(client):
    assert client.post("/api/events", json={"session_id": "nope", "field": "like", "value": 1}).status_code == 404

def test_discovery_failure_is_graceful(client, monkeypatch):
    def boom(url): raise ConnectionError("offline")
    monkeypatch.setattr(discovery, "fetch", boom)
    r = client.post("/api/policies/IN/discover").json()["results"][0]
    assert r["status"] == "fetch_failed"
    assert client.post("/api/policies/ZZ/discover").json()["results"][0]["status"] == "no_registered_source"

def test_structuring_requires_source(client):
    from app import db
    db.x("DELETE FROM sources WHERE jurisdiction='EU'")
    assert client.post("/api/policies/EU/structure").json()["code"] == "no_source_text"

def test_missing_key_fails_loudly_and_never_leaks(client, monkeypatch):
    monkeypatch.delenv("OPENROUTER_API_KEY")
    r = client.post("/api/policies/IN/structure").json()
    assert r["ok"] is False and r["code"] == "llm_unavailable" and "OPENROUTER_API_KEY" in r["message"]
    st = client.get("/api/llm/status").json()
    assert st["configured"] is False and st["provider"] == "openrouter" and st["model"] == "openrouter/free"
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-secret-123")
    assert "sk-secret-123" not in client.get("/api/llm/status").text + client.get("/api/health").text

def test_llm_output_is_validated_not_trusted(client, monkeypatch):
    import json
    monkeypatch.setattr(discovery, "fetch", lambda u: (200, "text/html", "<html><body>" + "Article 5 data minimisation. " * 20 + "</body></html>"))
    assert client.post("/api/policies/EU/discover").json()["results"][0]["status"] == "ok"
    monkeypatch.setattr(structuring, "call_llm", lambda p: "Here you go:\n" + json.dumps({"rules": [{"field": "email", "action": "ALLOW", "method": "pass", "ref": "Art 5"}]}))
    r = client.post("/api/policies/EU/structure").json()
    assert not r["ok"] and r["status"] == "rejected"
    assert client.post(f"/api/policies/{r['policy_id']}/activate").status_code == 422
    good = {"rules": [{"field": "email", "action": "REDACT", "method": "redact", "ref": "Art 5(1)(c)"}]}
    monkeypatch.setattr(structuring, "call_llm", lambda p: json.dumps(good))
    r2 = client.post("/api/policies/EU/structure").json()
    assert r2["ok"] and r2["status"] == "valid_candidate"
    assert client.post(f"/api/policies/{r2['policy_id']}/activate").status_code == 200
    s = client.post("/api/session", json={"region_override": "EU"}).json()["session_id"]
    assert client.get(f"/api/session/{s}").json()["policy"]["origin"] == "llm"
    monkeypatch.setattr(structuring, "call_llm", lambda p: "not json")
    assert client.post("/api/policies/EU/structure").json()["code"] == "llm_bad_output"

def test_validate_endpoint(client):
    assert client.post("/api/policies/validate", json={"policy": {"rules": []}}).json()["valid"] is False
