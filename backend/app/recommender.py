"""Simulated recommender. The API only ever calls profile(..., protected=True); the raw path exists for offline evaluation (metrics.py)."""
from .catalog import POSTS
from .transforms import category_of

W = {"like": 3, "save": 4, "follow": 2, "share": 2, "repost": 2, "comment": 2, "caption": 2, "story_view": 1, "profile_visit": 1, "hashtag": 1}

def profile(rows, protected=True):
    s = {}
    def add(c, v):
        if c: s[c] = s.get(c, 0) + v
    for r in rows:
        if protected and r["action"] == "BLOCK": continue
        val = r["protected"] if protected else r["original"]
        f = r["field"]
        if f in W: add(r["ctx_cat"], W[f])
        elif f == "watch_time":
            try: sec = r["signal"] if protected else float(r["original"])
            except (TypeError, ValueError): sec = 0
            add(r["ctx_cat"], .2 * (sec or 0))
        elif f in ("search", "skills", "job_interest"): add(category_of(val), 2)
    return s

def top_k(prof, k=5):
    ranked = sorted(POSTS, key=lambda p: (-prof.get(p["cat"], 0), int(p["id"][1:])))
    return [{**p, "score": round(prof.get(p["cat"], 0), 2)} for p in ranked[:k]]
