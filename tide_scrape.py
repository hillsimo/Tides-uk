import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone

def fetch_tide_levels():
    url = "https://www.tidetimes.co.uk/scarborough-tide-times"
    response = requests.get(url, timeout=10)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", {"class": "tideTable"})
    if not table:
        raise ValueError("Tide table not found on page")

    rows = table.find_all("tr")[1:]
    now = datetime.now(timezone.utc)
    levels = []

    for row in rows:
        cells = [c.get_text(strip=True) for c in row.find_all("td")]
        if len(cells) < 3:
            continue

        time_str, tide_type, height_str = cells[:3]
        try:
            height = float(height_str.replace("m", "").strip())
        except ValueError:
            continue

        local_time = datetime.strptime(time_str, "%H:%M")
        dt = datetime(now.year, now.month, now.day, local_time.hour, local_time.minute)
        dt = dt.replace(tzinfo=timezone.utc)

        levels.append({"time": dt, "height": height})

    extended = []
    for i in range(0, 2):
        for entry in levels:
            extended.append({
                "time": entry["time"] + timedelta(days=i),
                "height": entry["height"]
            })

    return extended
