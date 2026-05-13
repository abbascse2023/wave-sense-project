def hotspot_zone(sst_temp: float) -> str:
    # Simple prototype rule (you can tune later)
    if sst_temp < 24:
        return "LOW"
    elif 24 <= sst_temp < 28:
        return "MEDIUM"
    else:
        return "HIGH"
