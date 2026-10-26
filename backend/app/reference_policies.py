"""Hand-authored ILLUSTRATIVE reference rules (offline snapshot). Not legal advice; verify against official texts."""
def _allow(*f): return [{"field": x, "action": "ALLOW", "method": "pass", "ref": "reference-snapshot: low-risk recommendation signal"} for x in f]
def _r(f, a, m, p=None): return {"field": f, "action": a, "method": m, "param": p, "ref": "reference-snapshot: data minimisation for recommendation purpose"}

def _policy(code, regulation, source, version, eff, name_rule, age_w, watch_w, geo_p):
    return {"jurisdiction": code, "regulation": regulation, "source": source, "version": version, "effective_date": eff, "retrieved_at": None,
            "rules": [*_allow("skills", "job_interest", "like", "save", "follow", "share", "education", "repost", "story_view"),
                      _r("email", "REDACT", "redact"), _r("phone", "REDACT", "redact"), _r("account_id", "TRANSFORM", "pseudonym"), name_rule,
                      _r("age", "TRANSFORM", "age_range", age_w), _r("city", "TRANSFORM", "region"), _r("watch_time", "TRANSFORM", "bucket", watch_w),
                      _r("search", "TRANSFORM", "category"), _r("resume", "BLOCK", "block"),
                      _r("comment", "TRANSFORM", "category"), _r("caption", "TRANSFORM", "category"), _r("hashtag", "TRANSFORM", "category"), _r("dm", "BLOCK", "block"),
                      _r("profile_visit", "TRANSFORM", "pseudonym"), _r("device", "TRANSFORM", "device_family"), _r("geo", "TRANSFORM", "precision", geo_p)]}

PS = _r("name", "TRANSFORM", "pseudonym"); RD = _r("name", "REDACT", "redact")
REFERENCE = [
    _policy("IN", "Digital Personal Data Protection Act, 2023", "MeitY (offline reference snapshot)", "Act No. 22 of 2023", None, PS, 5, 5, 1),
    _policy("EU", "General Data Protection Regulation (EU) 2016/679", "EUR-Lex (offline reference snapshot)", "Applicable since 2018-05-25", "2018-05-25", RD, 10, 10, 0),
    _policy("US-CA", "California Consumer Privacy Act as amended by CPRA", "CPPA (offline reference snapshot)", "CCPA 2020; CPRA amendments 2023", "2020-01-01", PS, 5, 5, 1)]
