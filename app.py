from flask import Flask, render_template_string
from tide_scrape import fetch_tide_levels
from tide_svg import generate_next24_svg
from datetime import datetime, timezone

app = Flask(__name__)

@app.route("/render")
def render_dashboard():
    try:
        levels = fetch_tide_levels()
    except Exception as e:
        print("Tide fetch error:", e)
        levels = []

    now = datetime.now(timezone.utc)
    svg_chart = generate_next24_svg(levels, now=now)

    html = f"""
    <html>
    <head>
        <meta charset="utf-8" />
        <style>
            body {{
                background: #f5f5f5;
                color: #111;
                font-family: 'Inter', sans-serif;
                margin: 0;
                padding: 10px;
            }}
            .card {{
                background: white;
                border-radius: 8px;
                padding: 12px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                width: 100%;
                max-width: 600px;
                margin: auto;
            }}
            h2 {{
                font-size: 16px;
                margin-bottom: 8px;
            }}
            .tide-chart {{
                text-align: center;
            }}
        </style>
    </head>
    <body>
        <div class="card">
            <h2>Scarborough Tides — Next 24 Hours</h2>
            <div class="tide-chart">{svg_chart}</div>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

@app.route("/")
def index():
    return "<h3>Tides-UK Flask app is running</h3>"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
