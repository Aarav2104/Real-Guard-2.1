import pytest
from app import llm

class R:
    def __init__(s, code=200, data=None, headers=None): s.status_code, s._d, s.headers = code, data, headers or {}
    def json(s):
        if s._d is None: raise ValueError("no json")
        return s._d
OK = {"choices": [{"message": {"content": '{"rules": []}'}}]}

def test_openrouter_request_shape(monkeypatch):
    seen = {}
    def post(url, json, headers, timeout): seen.update(url=url, body=json, headers=headers); return R(200, OK)
    monkeypatch.setattr(llm.httpx, "post", post)
    monkeypatch.setenv("OPENROUTER_FALLBACK_MODELS", "a/b:free, c/d:free")
    assert llm.complete("hi") == '{"rules": []}'
    assert seen["url"] == "https://openrouter.ai/api/v1/chat/completions"
    assert seen["headers"]["Authorization"] == "Bearer test-key-not-real"
    assert seen["body"]["model"] == "openrouter/free" and seen["body"]["models"] == ["openrouter/free", "a/b:free", "c/d:free"]
    assert seen["body"]["messages"][-1] == {"role": "user", "content": "hi"}

def test_model_is_configurable(monkeypatch):
    seen = {}
    monkeypatch.setattr(llm.httpx, "post", lambda url, json, headers, timeout: seen.update(m=json["model"]) or R(200, OK))
    monkeypatch.setenv("OPENROUTER_MODEL", "some/model:free"); llm.complete("x"); assert seen["m"] == "some/model:free"

def test_generic_openai_compatible_provider(monkeypatch):
    seen = {}
    monkeypatch.setattr(llm.httpx, "post", lambda url, json, headers, timeout: seen.update(u=url, h=headers) or R(200, OK))
    for k, v in {"LLM_PROVIDER": "openai_compatible", "LLM_BASE_URL": "http://localhost:9/v1/", "LLM_API_KEY": "k", "LLM_MODEL": "m"}.items(): monkeypatch.setenv(k, v)
    llm.complete("x"); assert seen["u"] == "http://localhost:9/v1/chat/completions" and seen["h"]["Authorization"] == "Bearer k"

@pytest.mark.parametrize("resp,code", [(R(401, {"error": {"message": "bad"}}), "llm_auth"), (R(200, {"error": {"message": "model gone"}}), "llm_error"),
                                         (R(500, None), "llm_error"), (R(200, {"choices": [{"message": {"content": "  "}}]}), "llm_bad_output")])
def test_errors_are_explicit(monkeypatch, resp, code):
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: resp)
    with pytest.raises(llm.LLMError) as e: llm.complete("x")
    assert e.value.code == code

def test_rate_limit_retries_once_then_reports(monkeypatch):
    calls = []; monkeypatch.setattr(llm.time, "sleep", lambda s: None)
    monkeypatch.setattr(llm.httpx, "post", lambda *a, **k: calls.append(1) or R(429, {}))
    with pytest.raises(llm.LLMError) as e: llm.complete("x")
    assert e.value.code == "llm_rate_limited" and len(calls) == 2

def test_network_failure_and_unknown_provider(monkeypatch):
    def boom(*a, **k): raise llm.httpx.ConnectError("x")
    monkeypatch.setattr(llm.httpx, "post", boom)
    with pytest.raises(llm.LLMError) as e: llm.complete("x")
    assert e.value.code == "llm_network"
    monkeypatch.setenv("LLM_PROVIDER", "nope")
    with pytest.raises(llm.LLMError) as e: llm.complete("x")
    assert e.value.code == "llm_config"
