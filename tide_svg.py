from datetime import datetime
from xml.sax.saxutils import escape

def generate_tide_chart(tides):
    """
    Generates a simple 24-hour SVG tide height chart
    from Admiralty or fallback tide data.
    """

    if not tides:
        return "<svg width='100%' height='200'><text x='10' y='20'>No data</text></svg>"

    # Convert times and heights to usable numeric values
    points = []
    for t in tides:
        try:
            dt = datetime.fromisoformat(t["time"])
            height = float(t["height"].replace(" m", ""))
            hour = dt.hour + dt.minute / 60
            points.append((hour, height))
        except Exception:
            continue

    if not points:
        return "<svg width='100%' height='200'><text x='10' y='20'>No valid tide data</text></svg>"

    # Normalize data
    xs = [p[0] for p in points]
    ys = [p[1] for p in points]
    min_y, max_y = min(ys), max(ys)
    h_range = max_y - min_y if max_y != min_y else 1

    # SVG scaling
    width, height = 600, 200
    path_points = []
    for (x, y) in points:
        px = (x / 24) * width
        py = height - ((y - min_y) / h_range * height)
        path_points.append(f"{px},{py}")
    path_d = "M " + " L ".join(path_points)

    # Draw SVG
    svg = f"""
    <svg viewBox="0 0 {width} {height}" xmlns="http://www.w3.org/2000/svg">
      <style>
        .axis {{ stroke:#888; stroke-width:0.5 }}
        .grid {{ stroke:#ddd; stroke-width:0.5 }}
        .tide-line {{ fill:none; stroke:#007BFF; stroke-width:2 }}
        text {{ font-family: system-ui; font-size: 10px; fill: #444 }}
      </style>
      <!-- Horizontal grid lines -->
      {''.join(f"<line class='grid' x1='0' y1='{y}' x2='{width}' y2='{y}' />" for y in range(0, height, 40))}
      <!-- Tide line -->
      <path d="{escape(path_d)}" class="tide-line" />
      <!-- Axes -->
      <line x1="0" y1="{height}" x2="{width}" y2="{height}" class="axis" />
      <line x1="0" y1="0" x2="0" y2="{height}" class="axis" />
    </svg>
    """

    return svg
