from flask import Flask, jsonify, Response
from tide_scrape import fetch_tide_levels
from tide_svg import generate_tide_chart
import os
from datetime import datetime

app = Flask(__name__)

@app.route("/")
def index():
    return "<h2>Tides-UK Service Running</h2><p>Visit /render for live output.</p>"

@app.route("/render")
def render_tides():
    # --- Fetch tide data ---
    tides = fetch_tide_levels()
    print("DEBUG tides:", tides)

    # --- Fallback if no data ---
    if not tides:
        print("⚠️ No tide data returned — using fallback sample data.")
        now = datetime.utcnow()
        tides = [
            {"type": "High", "time": now.isoformat(), "height": "4.52 m"},
            {"type": "Low", "time": (now.replace(hour=(now.hour+6)%24)).isoformat(), "height": "1.02 m"},
            {"type": "High", "time": (now.replace(hour=(now.hour+12)%24)).isoformat(), "height": "4.40 m"},
            {"type": "Low", "time": (now.replace(hour=(now.hour+18)%24)).isoformat(), "height": "1.20 m"}
        ]

    # --- Generate SVG chart ---
    try:
        svg_chart = generate_tide_chart(tides)
    except Exception as e:
        print("⚠️ Error generating SVG:", e)
        svg_chart = "<svg><text x='10' y='20'>Tide chart unavailable</text></svg>"

    # --- Simple HTML display ---
    html = f"""
    <html>
      <head>
        <meta charset="utf-8"/>
        <title>Scarborough Tides</title>
        <style>
          body {{
            font-family: system-ui, sans-serif;
            background: #f9fafb;
            color: #111;
            text-align: center;
            margin: 0;
            padding: 2em;
          }}
          h1 {{ font-size: 1.5em; margin-bottom: 0.5em; }}
          table {{
            margin: 1em auto;
            border-collapse: collapse;
          }}
          td {{
            padding: 4px 8px;
            border-bottom: 1px solid #ddd;
            text-align: left;
          }}
          .chart {{
            max-width: 600px;
            margin: 2em auto;
          }}
        </style>
      </head>
      <body>
        <h1>Scarborough Tides – Next 24 Hours</h1>
        <div class="chart">{svg_chart}</div>
        <table>
          <tr><th>Type</th><th>Time (UTC)</th><th>Height</th></tr>
          {''.join(f"<tr><td>{t['type']}</td><td>{t['time'][11:16]}</td><td>{t['height']}</td></tr>" for t in tides)}
        </table>
      </body>
    </html>
    """

    return Response(html, mimetype="text/html")

@app.route("/api")
def api_tides():
    """Return tide data as JSON"""
    tides = fetch_tide_levels()
    return jsonify(tides or [])

# --- Render / Local port handling ---
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
