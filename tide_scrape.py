import os
import requests
from datetime import datetime, timedelta, timezone

API_KEY = os.getenv("WORLD_TIDES_KEY")
# Scarborough coordinates
LAT, LON = 54.283, -0.396

def fetch_tide_levels():
    """Fetch Scarborough tide data from WorldTides API"""
    if not API_KEY:
        print("❌ WORLD_TIDES_KEY not set.")
        return []

    now = datetime.now(timezone.utc)
    to_time = now + timedelta(hours=24)

    url = (
        f"https://www.worldtides.info/api/v3?extremes&lat={LAT}&lon={LON}"
        f"&start={int(now.timestamp())}&length=86400&key={API_KEY}"
    )

    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print("❌ Error fetching from WorldTides:", e)
        return []

    tides = []
    for event in data.get("extremes", []):
        tide_type = event["type"]
        tide_time = datetime.fromtimestamp(event["dt"], tz=timezone.utc)
        height = round(event.get("height", 0), 2)
        tides.append({
            "type": tide_type.title(),
            "time": tide_time.isoformat(),
            "height": f"{height:.2f} m"
        })

    print(f"✅ Loaded {len(tides)} tide entries from WorldTides.")
    return tides
