"""Evaluation metrics computed from stored events. Formulas are documented in the README."""
from .recommender import profile, top_k

RESIDUAL = {"pass": 1.0, "redact": 0.0, "block": 0.0, "pseudonym": 0.4, "age_range": 0.3, "region": 0.3, "bucket": 0.3, "category": 0.3, "device_family": 0.3, "precision": 0.3}

def compute(rows):
    counts = {"ALLOW": 0, "TRANSFORM": 0, "REDACT": 0, "BLOCK": 0}
    by_class, lat, base, prot = {}, [], 0.0, 0.0
    for r in rows:
        counts[r["action"]] += 1
        by_class.setdefault(r["classification"], {"ALLOW": 0, "TRANSFORM": 0, "REDACT": 0, "BLOCK": 0})[r["action"]] += 1
        base += r["weight"]; prot += r["weight"] * RESIDUAL.get(r["method"], 1.0); lat.append(r["latency_ms"])
    p_raw, p_prot = profile(rows, protected=False), profile(rows, protected=True)
    t_raw, t_prot = top_k(p_raw), top_k(p_prot)
    best = sum(p_raw.get(p["cat"], 0) for p in t_raw); got = sum(p_raw.get(p["cat"], 0) for p in t_prot)
    lat.sort()
    return {"records": len(rows), "counts": counts, "by_class": by_class, "risk_before": round(base, 2), "risk_after": round(prot, 2),
            "risk_reduction_pct": round((base - prot) / base * 100, 2) if base else None,
            "utility_retained_pct": round(got / best * 100, 2) if best else None,
            "top5_overlap": len({p["id"] for p in t_raw} & {p["id"] for p in t_prot}),
            "latency_avg_ms": round(sum(lat) / len(lat), 4) if lat else 0, "latency_p95_ms": round(lat[int(.95 * (len(lat) - 1))], 4) if lat else 0,
            "recs_raw": t_raw, "recs_protected": t_prot}
