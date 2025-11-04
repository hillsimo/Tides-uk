# Scarborough Coastal Conditions (trmnl plugin)

This repository contains a small Flask app that serves a weather + tide dashboard for Scarborough (Celsius).

Endpoints:
- `/healthz` — health check
- `/dashboard` — JSON payload (Open-Meteo + Admiralty)
- `/render` — HTML dashboard (ready to embed/display)

Environment variables:
- `ADMIRALTY_API_KEY` (required) — your Admiralty API subscription key
- `STATION_ID` (optional) — default is Admiralty ID for Scarborough (0158)

Run locally:
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export ADMIRALTY_API_KEY=your_key_here
python app.py
```

Deploy on Render:
1. Create a new Web Service on Render from this GitHub repo.
2. Set the build command to `pip install -r requirements.txt` and start command to `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2` (or use Docker).
3. Add environment variable `ADMIRALTY_API_KEY` in Render's dashboard.
