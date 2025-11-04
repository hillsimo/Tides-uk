from datetime import datetime, timedelta
import math

def generate_next24_svg(levels, now=None):
    """
    Generate a clean SVG tide height chart for the next 24 hours.
    Expects levels = list of dicts like:
      { "type": "High", "time": ISO string, "height": "5.42m" }
    """
    if not levels:
        return '<svg width="600" height="140" xmlns="http://www.w3.org/2000/svg"><text x="20" y="80">No tide data</text></svg>'

    now = now or datetime.utcnow()
    next24 = now + timedelta(hours=24)

    # Parse levels
    parsed = []
    for e in levels:
        try:
            t = datetime.fromisoformat(e["time"])
            h_str = e["height"].replace("m", "").strip()
            h = float(h_str) if h_str else None
            if h is not None and now <= t <= next24:
                parsed.append((t, h))
        except Exception:
            continue

    if not parsed:
        return '<svg width="600" height="140" xmlns="http://www.w3.org/2000/svg"><text x="20" y="80">No valid tide points</text></svg>'

    # Sort by time
    parsed.sort(key=lambda x: x[0])

    # SVG layout constants
    width, height = 600, 160
    margin, graph_h = 40, 100
    min_h = min(h for _, h in parsed)
    max_h = max(h for _, h in parsed)
    range_h = max_h - min_h or 1

    # Scale functions
    def x_pos(t):
        return margin + ((t - now).total_seconds() / (24 * 3600)) * (width - 2 * margin)

    def y_pos(h):
        return height - margin - ((h - min_h) / range_h) * graph_h

    # Build path for line chart
    path = "M " + " ".join(f"{x_pos(t):.1f},{y_pos(h):.1f}" for t, h in parsed)

    # Axis + labels
    y_ticks = [round(min_h + i * range_h / 4, 2) for i in range(5)]

    svg = f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">'
    svg += '<rect width="100%" height="100%" fill="white"/>'

    # Horizontal grid lines
    for yv in y_ticks:
        y = y_pos(yv)
        svg += f'<line x1="{margin}" y1="{y:.1f}" x2="{width-margin}" y2="{y:.1f}" stroke="#ddd" stroke-width="1"/>'

    # Tide line
    svg += f'<path d="{path}" fill="none" stroke="#0077cc" stroke-width="2"/>'

    # Tide height axis (left)
    for yv in y_ticks:
        y = y_pos(yv)
        svg += f'<text x="4" y="{y+4:.1f}" font-size="10" fill="#333">{yv:.2f}</text>'

    # Time labels (every 6 hours)
    for h in range(0, 25, 6):
        x = margin + (h / 24) * (width - 2 * margin)
        label = (now + timedelta(hours=h)).strftime("%H:%M")
        svg += f'<text x="{x-12:.1f}" y="{height-8}" font-size="10" fill="#555">{label}</text>'

    svg += "</svg>"
    return svg
