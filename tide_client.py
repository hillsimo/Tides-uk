import os, requests
from datetime import datetime, timedelta, timezone

class TideClient:
    BASE_URL = "https://admiraltyapi.azure-api.net/uktidalapi/api/V1/Stations"

    def __init__(self, api_key=None):
        self.api_key = api_key or os.getenv("ADMIRALTY_API_KEY")

    def _headers(self):
        return {"Ocp-Apim-Subscription-Key": self.api_key} if self.api_key else {}

    def station_search(self, name):
        url = f"{self.BASE_URL}/FindByName/{name}"
        r = requests.get(url, headers=self._headers(), timeout=10)
        r.raise_for_status()
        return r.json()

    def get_tides(self, station=None, station_id=None, hours=24):
        if station_id is None and station:
            matches = self.station_search(station)
            if not matches or "Stations" not in matches or len(matches["Stations"]) == 0:
                raise ValueError(f"No station found for {station}")
            station_id = matches["Stations"][0].get("StationId")
            if not station_id:
                raise ValueError("StationId missing")
        if station_id is None:
            raise ValueError("station_id required")

        now = datetime.now(timezone.utc)
        start = now
        end = now + timedelta(hours=hours)

        params = {"fromdate": start.isoformat(), "todate": end.isoformat()}

        # Tidal events (high/low)
        url_events = f"{self.BASE_URL}/{station_id}/Predictions/TidalEvents"
        r = requests.get(url_events, headers=self._headers(), params=params, timeout=10)
        r.raise_for_status()
        events = r.json()

        # High-resolution levels for graph
        url_levels = f"{self.BASE_URL}/{station_id}/Predictions/TidalLevels"
        r2 = requests.get(url_levels, headers=self._headers(), params=params, timeout=10)
        r2.raise_for_status()
        levels = r2.json()

        evs = []
        for e in events if isinstance(events, list) else (events.get('Predictions') or []):
            dt = e.get('DateTime') or e.get('Time')
            try:
                h = float(e.get('Height')) if e.get('Height') is not None else None
            except Exception:
                h = None
            evs.append({
                'dateTime': dt,
                'eventType': e.get('EventType'),
                'height': h
            })

        lvls = []
        preds = levels.get('Predictions') if isinstance(levels, dict) else levels
        if preds is None:
            preds = levels
        for p in preds if isinstance(preds, list) else []:
            dt = p.get('Time') or p.get('DateTime')
            try:
                h = float(p.get('Height') or p.get('Value')) if (p.get('Height') or p.get('Value')) is not None else None
            except Exception:
                h = None
            lvls.append({'time': dt, 'height': h})

        # sort levels by time
        lvls = sorted([L for L in lvls if L['time'] and L['height'] is not None], key=lambda x: x['time'])
        evs = [e for e in evs if e['dateTime'] is not None]

        next_ev = None
        for e in evs:
            try:
                t = datetime.fromisoformat(e['dateTime'].replace('Z', '+00:00'))
                if t > now:
                    next_ev = e
                    break
            except Exception:
                continue

        return {
            'station_id': station_id,
            'from': start.isoformat(),
            'to': end.isoformat(),
            'events': evs,
            'levels': lvls,
            'next_event': next_ev
        }
