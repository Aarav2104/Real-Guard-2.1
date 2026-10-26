"""Metadata classification. Extensible: add a field to FIELD_CLASS or a pattern to PATTERNS."""
import re
WEIGHT = {"DIRECT_IDENTIFIER": 10, "SENSITIVE_DATA": 9, "QUASI_IDENTIFIER": 5, "LOCATION_DATA": 5,
          "BEHAVIORAL_DATA": 2, "RECOMMENDATION_SIGNAL": 1, "ADVERTISEMENT_DATA": 3, "UNCLASSIFIED": 3}
FIELD_CLASS = {
    "account_id": "DIRECT_IDENTIFIER", "name": "DIRECT_IDENTIFIER", "email": "DIRECT_IDENTIFIER",
    "phone": "DIRECT_IDENTIFIER", "age": "QUASI_IDENTIFIER", "education": "QUASI_IDENTIFIER",
    "city": "LOCATION_DATA", "resume": "SENSITIVE_DATA", "skills": "RECOMMENDATION_SIGNAL",
    "job_interest": "RECOMMENDATION_SIGNAL", "watch_time": "BEHAVIORAL_DATA", "search": "BEHAVIORAL_DATA",
    "like": "RECOMMENDATION_SIGNAL", "save": "RECOMMENDATION_SIGNAL", "follow": "RECOMMENDATION_SIGNAL",
    "share": "RECOMMENDATION_SIGNAL",
    "repost": "RECOMMENDATION_SIGNAL", "story_view": "RECOMMENDATION_SIGNAL", "profile_visit": "BEHAVIORAL_DATA", "hashtag": "BEHAVIORAL_DATA",
    "comment": "SENSITIVE_DATA", "caption": "SENSITIVE_DATA", "dm": "SENSITIVE_DATA", "device": "QUASI_IDENTIFIER", "geo": "LOCATION_DATA"}
PATTERNS = [(re.compile(r"^[^@\s]+@[^@\s]+\.\w+$"), "DIRECT_IDENTIFIER"),
            (re.compile(r"^\+?[\d\s\-()]{8,16}$"), "DIRECT_IDENTIFIER")]

def classify(field, value=None):
    """Return (category, weight). Unknown fields fall back to value patterns, then UNCLASSIFIED."""
    cat = FIELD_CLASS.get(field)
    if not cat and value is not None:
        cat = next((c for p, c in PATTERNS if p.match(str(value))), None)
    cat = cat or "UNCLASSIFIED"
    return cat, WEIGHT[cat]
