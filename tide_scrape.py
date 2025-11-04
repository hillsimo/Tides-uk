import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

TIDE_URL = "https://www.tidetimes.co.uk/scarborough-tide-times"

def fetch_tide_levels():
    '''Scrape Scarborough tide data from tidetimes.co.uk'''
    try:
        r = requests.get(TIDE_URL, timeout=10)
        r.raise_for_status()
    except Exception as e:
        print("❌ Error fetching tide data:", e)
        return []

    soup = BeautifulSoup(r.text, "html.parser")

    tide_rows = soup.select("table.tidetimes tr")
    tides = []
    for row in tide_rows:
        cols = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cols) >= 2 and ("High" in cols[0] or "Low" in cols[0]):
            try:
                tide_type = cols[0]
                tide_time = cols[1]
                tide_height = cols[2] if len(cols) > 2 else ""

                # Convert time to datetime
                t = datetime.strptime(tide_time, "%I:%M%p")
                now = datetime.now(timezone.utc)
                tide_dt = now.replace(hour=t.hour, minute=t.minute, second=0, microsecond=0)

                tides.append({
                    "type": tide_type,
                    "time": tide_dt.isoformat(),
                    "height": tide_height
                })
            except Exception:
                continue

    print(f"✅ Scraped {len(tides)} tide entries.")
    return tides
