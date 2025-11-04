import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

TIDE_URL = "https://www.tidetimes.co.uk/scarborough-tide-times"

def fetch_tide_levels():
    """Scrape tide data for Scarborough from tidetimes.co.uk"""
    try:
        r = requests.get(TIDE_URL, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print("❌ Error fetching tide data:", e)
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    # Find the main tide table — usually the first <table> under .tideTable
    table = soup.select_one("table.tidetimes") or soup.find("table")

    if not table:
        print("❌ Could not find tide table.")
        return []

    tides = []
    rows = table.find_all("tr")
    for row in rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) >= 2:
            event_type = cols[0]
            event_time = cols[1]
            event_height = cols[2] if len(cols) > 2 else ""

            if any(k in event_type.lower() for k in ["high", "low"]):
                try:
                    # Parse time like "01:24am" → datetime
                    t = datetime.strptime(event_time.lower(), "%I:%M%p")
                    now = datetime.now(timezone.utc)
                    tide_dt = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)
                    tides.append({
                        "type": event_type.title(),
                        "time": tide_dt.isoformat(),
                        "height": event_height
                    })
                except Exception as e:
                    print("⚠️ Parse error:", e)
                    continue

    print(f"✅ Scraped {len(tides)} tide entries.")
    return tides
