from datetime import datetime, timedelta, timezone
import math

def generate_next24_svg(levels, now=None, width=600, height=220):
    if now is None:
        now = datetime.now(timezone.utc)

    start = now
    end = now + timedelta(hours=24)

    pts = [(l['time'].timestamp(), l['height']) for l in levels if 'height' in l]
    if not pts:
        return f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg"><text x="10" y="{height/2}" fill="#000">No tide data</text></svg>'

    pts.sort()
    min_h = min(h for _, h in pts)
    max_h = max(h for _, h in pts)

    pad = max(0.5, (max_h - min_h) * 0.1)
    min_display = math.floor(min_h - pad)
    max_display = math.ceil(max_h + pad)

    def x_for_time(ts):
        return 70 + ((ts - start.timestamp()) / (end.timestamp() - start.timestamp())) * (width - 90)

    def y_for_height(h):
        frac = (h - min_display) / (max_display - min_display)
        return 20 + (1 - frac) * (height - 60)

    svg = [f'<svg width="{width}" height="{height}" xmlns="http://www.w3.org/2000/svg">',
           f'<rect width="{width}" height="{height}" fill="#fff"/>']

    # grid lines
    for gv in range(int(min_display), int(max_display) + 1):
        y = y_for_height(gv)
        svg.append(f'<line x1="70" y1="{y:.2f}" x2="{width-20}" y2="{y:.2f}" stroke="#ccc" stroke-width="1"/>')
        svg.append(f'<text x="10" y="{y+4:.2f}" font-size="12" fill="#333">{gv:.2f}m</text>')

    # line path
    points = " ".join(f"{x_for_time(ts):.2f},{y_for_height(h):.2f}" for ts, h in pts)
    svg.append(f'<polyline fill="none" stroke="#000" stroke-width="2" points="{points}" />')
    svg.append('</svg>')
    return "\n".join(svg)
