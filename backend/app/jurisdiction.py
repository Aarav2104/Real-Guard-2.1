"""Automatic jurisdiction detection from session signals. Extend the tables to add jurisdictions."""
TZ_TO_CODE = {"Asia/Kolkata": "IN", "Asia/Calcutta": "IN", "America/Los_Angeles": "US-CA"}
EU_TZ = {"Europe/" + c for c in ("Berlin Paris Madrid Rome Amsterdam Brussels Vienna Dublin Lisbon Warsaw Stockholm Helsinki "
         "Athens Prague Budapest Copenhagen Bucharest Sofia Zagreb Luxembourg Tallinn Riga Vilnius Bratislava Ljubljana Valletta").split()}
EU_COUNTRIES = set("AT BE BG HR CY CZ DK EE FI FR DE GR HU IE IT LV LT LU MT NL PL PT RO SK SI ES SE".split())
LANG_REGION_TO_CODE = {"IN": "IN"}

def detect(tz=None, lang=None, override=None):
    region = (lang or "").replace("_", "-").split("-")[1].upper() if "-" in (lang or "").replace("_", "-") else ""
    signals = {"platform_region": override, "timezone": tz, "language_region": region or None}
    if override and override != "auto":
        return {"code": override.upper() if override.upper() != "UNKNOWN" else "UNKNOWN", "source": "platform region signal",
                "resolved": override.upper() != "UNKNOWN", "signals": signals}
    if tz in TZ_TO_CODE: return {"code": TZ_TO_CODE[tz], "source": f"session timezone ({tz})", "resolved": True, "signals": signals}
    if tz in EU_TZ: return {"code": "EU", "source": f"session timezone ({tz})", "resolved": True, "signals": signals}
    if region in EU_COUNTRIES: return {"code": "EU", "source": f"language region ({region})", "resolved": True, "signals": signals}
    if region in LANG_REGION_TO_CODE: return {"code": LANG_REGION_TO_CODE[region], "source": f"language region ({region})", "resolved": True, "signals": signals}
    return {"code": "UNKNOWN", "source": "no reliable signal", "resolved": False, "signals": signals}
