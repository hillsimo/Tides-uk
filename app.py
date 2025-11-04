import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

def fetch_tide_levels():
    url = "https://www.tidetimes.co.uk/scarborough-tide-times"
    response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Look for any tide table, not just class='tideTable'
    table = soup.find("table")
    if not table:
        raise ValueError("Could not locate tide table on tidetimes.co.uk")

    rows = table.find_all("tr")
    levels = []
    now = datetime.now(timezone.utc)

    for row in rows:
        cols = [td.get_text(strip=True) for td in row.find_all("td")]
        if len(cols) < 3:
            continue

        time_str, tide_type, height_str = cols[:3]
        if not ("high" in tide_type.lower() or "low" in tide_type.lower()):
            continue

        try:
            height = float(height_str.lower().replace("m", "").strip())
        except ValueError:
            continue

        # Parse time and assume today’s date
        try:
            local_time = datetime.strptime(time_str, "%H:%M")
        except ValueError:
            continue

        dt = datetime(now.year, now.month, now.day, local_time.hour, local_time.minute, tzinfo=timezone.utc)
        levels.append({"time": dt, "height": height})

    # Extend data to cover 24 hours ahead
    extended = []
    for i in range(2):
        for entry in levels:
            extended.append({
                "time": entry["time"] + timedelta(days=i),
                "height": entry["height"]
            })

    if not extended:
        print("⚠️ No tide entries parsed — check HTML structure.")
    return extended
