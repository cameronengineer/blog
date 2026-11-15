#!/usr/bin/env python3
"""Extract a public route from a FIT file, excluding health and device fields.

One-time import: .venv/bin/pip install fitdecode==0.11.0
.venv/bin/python scripts/import_hike.py activity.fit static/posts/post-slug
The regular site build does not need fitdecode or the original FIT file.
"""
import argparse
from html import escape
import json
import math
from pathlib import Path

import fitdecode


def import_route(source, output):
    points = []
    session = {}
    with fitdecode.FitReader(source) as fit:
        for frame in fit:
            if not isinstance(frame, fitdecode.FitDataMessage):
                continue
            fields = {f.name: f.value for f in frame.fields}
            if frame.name == 'session':
                session = fields
            if frame.name != 'record':
                continue
            lat, lon = fields.get('position_lat'), fields.get('position_long')
            elevation = fields.get('enhanced_altitude', fields.get('altitude'))
            distance = fields.get('distance')
            if None in (lat, lon, elevation, distance):
                continue
            if abs(lat) >= 2**31 or abs(lon) >= 2**31:
                continue
            points.append([round(lon * 180 / 2**31, 6), round(lat * 180 / 2**31, 6),
                           round(elevation, 1), round(distance / 1000, 4)])
    if len(points) < 2:
        raise ValueError('FIT file needs GPS positions, elevation and distance records')
    highest = max(range(len(points)), key=lambda i: points[i][2])
    # Retain the highest point and both endpoints, while reducing the map payload.
    selected = sorted(set(range(0, len(points), 4)) | {highest, len(points) - 1})
    track = [points[i] for i in selected]
    summary = {
        'date': str(session['start_time'].date()),
        'distanceKm': round(session['total_distance'] / 1000, 2),
        'ascentM': session['total_ascent'],
        'descentM': session['total_descent'],
        'elapsedSeconds': round(session['total_elapsed_time']),
        'minElevationM': min(p[2] for p in points),
        'maxElevationM': max(p[2] for p in points),
        'highestIndex': selected.index(highest),
        'bounds': [[min(p[0] for p in points), min(p[1] for p in points)],
                   [max(p[0] for p in points), max(p[1] for p in points)]],
    }
    data = {'summary': summary, 'coordinates': [p[:3] for p in track],
            'distanceKm': [p[3] for p in track]}
    output.mkdir(parents=True, exist_ok=True)
    (output / 'route.json').write_text(json.dumps(data, separators=(',', ':')) + '\n')

    def svg(content, title, height):
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 {height}" role="img"><title>{escape(title)}</title><rect width="800" height="{height}" fill="#f7f4ec"/>{content}</svg>\n'

    # An offline route outline remains visible if WebGL or map tiles cannot load.
    west, south = summary['bounds'][0]
    east, north = summary['bounds'][1]
    aspect = math.cos(math.radians((south + north) / 2))
    scale = min(640 / ((east - west) * aspect), 350 / (north - south))
    center_lon, center_lat = (east + west) / 2, (north + south) / 2
    xy = lambda p: (400 + (p[0] - center_lon) * aspect * scale, 245 - (p[1] - center_lat) * scale)
    polyline = ' '.join(f'{x:.1f},{y:.1f}' for x, y in map(xy, track))
    start_x, start_y = xy(track[0])
    high_x, high_y = xy(track[summary['highestIndex']])
    outline = f'<text x="30" y="36" fill="#626c62" font-family="system-ui,sans-serif" font-size="13">Recorded route · north up</text><text x="758" y="38" fill="#243d32" font-size="20">↑ N</text><polyline points="{polyline}" fill="none" stroke="#2f5948" stroke-width="3" stroke-linejoin="round"/><circle cx="{start_x}" cy="{start_y}" r="6" fill="#2f5948"/><text x="{start_x + 12}" y="{start_y - 12}" font-size="14" fill="#243d32">Start / finish</text><circle cx="{high_x}" cy="{high_y}" r="6" fill="#946a2f"/><text x="{high_x - 10}" y="{high_y + 28}" text-anchor="end" font-size="14" fill="#243d32">Highest recorded point · {summary["maxElevationM"]:,.0f} m</text>'
    (output / 'route.svg').write_text(svg(outline, 'GPS route outline, north up', 480))
    x = lambda d: 64 + d / summary['distanceKm'] * 712
    y = lambda e: 170 - (e - 1400) / 2200 * 140
    path = ' '.join(f'{x(p[3]):.1f},{y(p[2]):.1f}' for p in track)
    profile = '<g font-family="system-ui,sans-serif" font-size="11" fill="#626c62">'
    for elevation in (1500, 2500, 3500):
        yy = y(elevation)
        profile += f'<path d="M64 {yy}H776" stroke="#d9ded2"/><text x="52" y="{yy+4}" text-anchor="end">{elevation:,}</text>'
    profile += f'<polygon points="64,170 {path} {x(track[-1][3])},170" fill="#e9eee5"/><polyline points="{path}" fill="none" stroke="#2f5948" stroke-width="2"/><text x="64" y="196">0 km</text><text x="776" y="196" text-anchor="end">{summary["distanceKm"]:.1f} km</text><text x="64" y="16">Elevation (m)</text></g>'
    (output / 'elevation.svg').write_text(svg(profile, 'Recorded elevation against distance', 210))
    print(json.dumps(summary, indent=2))
    print(f'Exported {len(track)} GPS points; no health or device data included.')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('source', type=Path)
    parser.add_argument('output', type=Path)
    args = parser.parse_args()
    import_route(args.source, args.output)
