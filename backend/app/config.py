"""Configuration from environment variables. No secrets live in code."""
import os, secrets
from pathlib import Path
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:  # python-dotenv is optional
    pass

BASE = Path(__file__).resolve().parent.parent
FRONTEND = BASE.parent / "frontend"
DB_PATH = Path(os.getenv("REALGUARD_DB", str(BASE / "data" / "realguard.db")))
# Key for HMAC pseudonyms. If unset a random key is used, so tokens change per restart.
PSEUDONYM_KEY = os.getenv("REALGUARD_PSEUDONYM_KEY") or secrets.token_hex(16)
HTTP_TIMEOUT = float(os.getenv("REALGUARD_HTTP_TIMEOUT", "10"))
