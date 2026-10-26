import os, tempfile, sys
from pathlib import Path
os.environ["REALGUARD_DB"] = str(Path(tempfile.mkdtemp()) / "t.db")
os.environ["REALGUARD_PSEUDONYM_KEY"] = "test-key"
os.environ["OPENROUTER_API_KEY"] = "test-key-not-real"
os.environ.pop("OPENROUTER_MODEL", None)
os.environ.pop("LLM_PROVIDER", None)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import pytest
from fastapi.testclient import TestClient

@pytest.fixture(scope="session")
def client():
    from app.main import app
    with TestClient(app) as c:
        yield c

@pytest.fixture()
def sid(client):
    return client.post("/api/session", json={"tz": "Asia/Kolkata", "lang": "en-IN"}).json()["session_id"]
