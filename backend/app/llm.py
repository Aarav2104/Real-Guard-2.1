"""Provider layer: the ONLY file that knows how to talk to an LLM provider.

Providers speak the OpenAI-compatible /chat/completions protocol, so switching provider or model is configuration, not code.
  LLM_PROVIDER=openrouter         (default) uses OPENROUTER_API_KEY / OPENROUTER_MODEL / OPENROUTER_BASE_URL
  LLM_PROVIDER=openai_compatible  uses LLM_API_KEY / LLM_MODEL / LLM_BASE_URL (Groq, Together, Gemini's OpenAI endpoint, local servers...)
Settings are read at call time. The key is never logged, returned by the API, or stored. There is no mock mode: a missing key is an error."""
import os, time
import httpx
from . import config  # noqa: F401  (importing config loads .env)

class LLMError(Exception):
    def __init__(self, code, message): super().__init__(message); self.code = code

def settings():
    p = os.getenv("LLM_PROVIDER", "openrouter").strip().lower()
    if p == "openrouter":
        return {"provider": p, "key_env": "OPENROUTER_API_KEY", "key": os.getenv("OPENROUTER_API_KEY", "").strip(),
                "model": os.getenv("OPENROUTER_MODEL", "openrouter/free").strip(), "base_url": os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1").rstrip("/"),
                "fallbacks": [m.strip() for m in os.getenv("OPENROUTER_FALLBACK_MODELS", "").split(",") if m.strip()],
                "headers": {k: v for k, v in {"HTTP-Referer": os.getenv("OPENROUTER_SITE_URL", ""), "X-Title": os.getenv("OPENROUTER_APP_NAME", "Real Guard")}.items() if v}}
    if p == "openai_compatible":
        return {"provider": p, "key_env": "LLM_API_KEY", "key": os.getenv("LLM_API_KEY", "").strip(), "model": os.getenv("LLM_MODEL", "").strip(),
                "base_url": os.getenv("LLM_BASE_URL", "").rstrip("/"), "fallbacks": [], "headers": {}}
    raise LLMError("llm_config", f"Unknown LLM_PROVIDER {p!r}. Use 'openrouter' or 'openai_compatible'.")

def status():
    """Safe to expose: never includes the key."""
    try: s = settings()
    except LLMError as e: return {"provider": os.getenv("LLM_PROVIDER"), "configured": False, "model": None, "error": str(e)}
    missing = [n for n, v in (("key", s["key"]), ("model", s["model"]), ("base_url", s["base_url"])) if not v]
    return {"provider": s["provider"], "model": s["model"] or None, "key_env": s["key_env"], "configured": not missing, "missing": missing}

def require_configured():
    s = settings()
    if not s["key"]:
        raise LLMError("llm_unavailable", f"{s['key_env']} is not set. Copy .env.example to backend/.env, add your key, and restart the server.")
    if not s["model"] or not s["base_url"]:
        raise LLMError("llm_config", "LLM_MODEL and LLM_BASE_URL are required when LLM_PROVIDER=openai_compatible.")
    return s

def complete(prompt):
    s = require_configured()
    body = {"model": s["model"], "temperature": 0, "max_tokens": 4000,
            "messages": [{"role": "system", "content": "You output only a single JSON object. No prose, no markdown."}, {"role": "user", "content": prompt}]}
    if s["fallbacks"]: body["models"] = [s["model"], *s["fallbacks"]]  # OpenRouter-side model fallback
    headers = {"Authorization": f"Bearer {s['key']}", "Content-Type": "application/json", **s["headers"]}
    for attempt in (1, 2):
        try: r = httpx.post(f"{s['base_url']}/chat/completions", json=body, headers=headers, timeout=60)
        except httpx.HTTPError as e: raise LLMError("llm_network", f"Could not reach {s['provider']} ({type(e).__name__}).")
        if r.status_code == 429 and attempt == 1:
            time.sleep(min(float(r.headers.get("retry-after", 2) or 2), 5)); continue
        break
    if r.status_code in (401, 403): raise LLMError("llm_auth", f"{s['provider']} rejected the API key (HTTP {r.status_code}). Check {s['key_env']}.")
    if r.status_code == 429: raise LLMError("llm_rate_limited", "Free-tier rate limit reached. Wait a minute, or set another OPENROUTER_MODEL / OPENROUTER_FALLBACK_MODELS.")
    try: data = r.json()
    except ValueError: raise LLMError("llm_error", f"{s['provider']} returned a non-JSON response (HTTP {r.status_code}).")
    if r.status_code != 200 or "error" in data:
        detail = (data.get("error") or {}).get("message") if isinstance(data.get("error"), dict) else None
        raise LLMError("llm_error", f"{s['provider']} error (HTTP {r.status_code}): {(detail or 'no detail')[:200]}")
    try: text = data["choices"][0]["message"]["content"]
    except (KeyError, IndexError, TypeError): text = None
    if not text or not str(text).strip(): raise LLMError("llm_bad_output", "The model returned an empty response; try again or choose another model.")
    return str(text)
