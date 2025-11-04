import os
import requests
from datetime import datetime, timedelta, timezone

ADMIRALTY_API_KEY = os.getenv("ADMIRALTY_API_KEY")
# Scarborough station ID (official code)
STATION_ID = "0158"

def fetch_tide_levels():
    """Fetch Scarborough tide events from the Admiralty UK Tidal API"""
    if not ADMIRALTY_API_KEY:
        print("❌ ADMIRALTY_API_KEY not set.")
        return []

    now = datetime.now(timezone.utc)
    from_date = now.isoformat()
    to_date = (now + timedelta(days=1)).isoformat()

    url = (
        f"https://admiraltyapi.azure-api.net/uktidalapi/api/V1/Stations/{STATION_ID}/"
        f"Predictions/TidalEvents?fromdate={from_date}&todate={to_date}"
    )

    headers = {"Ocp-Apim-Subscription-Key": ADMIRALTY_API_KEY}

    try:
        resp = requests.get(url, headers=headers, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except Exception as e:
        print("❌ Error fetching Admiralty data:", e)
        return []

    tides = []
    for event in data:
        try:
            dt = datetime.fromisoformat(event["DateTime"])
            height = round(event["Height"], 2)
            tides.append({
                "type": event["EventType"],
                "time": dt.isoformat(),
                "height": f"{height:.2f} m"
            })
        except Exception:
            continue

    print(f"✅ Fetched {len(tides)} Admiralty tide events.")
    return tides
