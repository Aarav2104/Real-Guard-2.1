"""Tiny SQLite layer (stdlib only)."""
import json, sqlite3, threading
from .config import DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS sessions(id TEXT PRIMARY KEY, tz TEXT, lang TEXT, region_override TEXT,
  jurisdiction TEXT, jurisdiction_source TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS events(id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT, field TEXT,
  original TEXT, source TEXT, purpose TEXT, ad_id TEXT, ctx_cat TEXT, ts TEXT, jurisdiction TEXT,
  policy_id TEXT, classification TEXT, weight REAL, action TEXT, method TEXT, rule TEXT, rule_ref TEXT,
  protected TEXT, signal REAL, latency_ms REAL);
CREATE TABLE IF NOT EXISTS policies(id TEXT PRIMARY KEY, jurisdiction TEXT, regulation TEXT, source TEXT,
  version TEXT, effective_date TEXT, retrieved_at TEXT, origin TEXT, status TEXT, validation TEXT,
  body TEXT, created_at TEXT);
CREATE TABLE IF NOT EXISTS sources(id INTEGER PRIMARY KEY AUTOINCREMENT, jurisdiction TEXT, name TEXT,
  url TEXT, fetched_at TEXT, status TEXT, http_status INTEGER, sha256 TEXT, text TEXT, error TEXT);
"""
_lock = threading.Lock()
_conn = None

def conn():
    global _conn
    if _conn is None:
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        _conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        _conn.row_factory = sqlite3.Row
        _conn.executescript(SCHEMA)
    return _conn

def q(sql, args=()):
    with _lock:
        return [dict(r) for r in conn().execute(sql, args).fetchall()]

def x(sql, args=()):
    with _lock:
        cur = conn().execute(sql, args)
        conn().commit()
        return cur.lastrowid

def dumps(o): return json.dumps(o, ensure_ascii=False)
