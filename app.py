from flask import Flask, jsonify, render_template, request, url_for
from tide_client import TideClient
import requests, os, datetime

app = Flask(__name__, template_folder="templates", static_folder="static")

API_KEY = os.getenv("ADMIRALTY_API_KEY")
STATION_ID = os.getenv("STATION_ID", "0158")  # Admiralty ID for Scarborough by default
tide = TideClient(api_key=API_KEY)

# Scarborough coords for Open-Meteo
LAT = 54.2808
LON = -0.4057
TZ = "Europe/London"

def fetch_weather():
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": LAT,
        "longitude": LON,
        "current_weather": "true",
        "daily": "temperature_2m_max,temperature_2m_min,weathercode",
        "timezone": TZ,
        "temperature_unit": "celsius"
    }
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()

@app.route("/healthz")
def health():
    return jsonify({"status": "ok", "station": "Scarborough"})

@app.route("/dashboard")
def dashboard():
    try:
        weather = fetch_weather()
    except Exception as e:
        weather = {"error": str(e)}
    try:
        tides = tide.get_tides(station_id=STATION_ID, hours=24)
    except Exception as e:
        tides = {"error": str(e)}
    combined = {
        "location": {"name": "Scarborough, UK", "latitude": LAT, "longitude": LON, "tz": TZ},
        "weather": weather,
        "tides": tides,
        "generated_at": datetime.datetime.utcnow().isoformat() + "Z"
    }
    return jsonify(combined)

@app.route("/render")
def render_dashboard():
    payload = requests.get(request.url_root.rstrip('/') + "/dashboard", timeout=10).json()
    weather = payload.get("weather", {})
    tides = payload.get("tides", {})
    return render_template("dashboard.html", weather=weather, tide=tides, loc="Scarborough")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
