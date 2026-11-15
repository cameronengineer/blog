#!/usr/bin/env python3
"""Prepare the Marmolada photos/videos and match capture times to the FIT track.

Optional authoring dependencies: Pillow, pillow-heif, fitdecode; ffmpeg on PATH.
Input metadata is ExifTool JSON with numeric GPS fields, DateTimeOriginal,
OffsetTimeOriginal and QuickTime CreationDate. Original files remain untouched.
"""
import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import re
import shutil
import subprocess
import tempfile

import fitdecode
from PIL import Image, ImageOps
import pillow_heif

SPECS = [
    ('IMG_1784.MOV', 'first-light', 'First light on the climb', 'the-climb', 'video', '1'),
    ('IMG_1788.heic', 'on-the-climb', 'Looking back down from the rocky ascent', 'the-climb', 'photo', '2'),
    ('IMG_1808.heic', 'summit', 'At the summit cross on Punta Penia', 'at-the-top', 'photo', '3'),
    ('IMG_1827.heif', 'summit-panorama', 'Panorama from Punta Penia, above the clouds', 'at-the-top', 'cover', None),
    ('IMG_1832.MOV', 'descent', 'Rock, snow and cloud beside the cables on the descent', 'the-descent', 'video', '4'),
    ('IMG_1837.heic', 'back-in-the-valley', 'Back at the car beneath the cable cars', 'the-descent', 'photo', '5'),
]


def encode_video(source, target):
    probe = json.loads(subprocess.check_output(['ffprobe', '-v', 'error', '-select_streams', 'v:0',
        '-show_entries', 'stream=color_transfer', '-of', 'json', str(source)]))
    transfer = probe['streams'][0].get('color_transfer')
    with tempfile.TemporaryDirectory(prefix='blog-video-') as temporary:
        video_source = source
        if transfer in ('arib-std-b67', 'smpte2084'):
            if not shutil.which('avconvert'):
                raise RuntimeError('HDR originals need macOS avconvert for the SDR authoring conversion')
            video_source = Path(temporary) / 'sdr.mp4'
            subprocess.run(['avconvert', '--source', str(source), '--preset', 'Preset1280x720',
                            '--output', str(video_source)], stdout=subprocess.DEVNULL, check=True)
        subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(video_source),
            '-map', '0:v:0', '-map', '0:a:0?', '-map_metadata', '-1', '-map_chapters', '-1',
            '-vf', 'scale=1280:1280:force_original_aspect_ratio=decrease:force_divisible_by=2,fps=30',
            '-c:v', 'libx264', '-preset', 'slow', '-crf', '25', '-maxrate', '2200k', '-bufsize', '4400k',
            '-pix_fmt', 'yuv420p', '-c:a', 'aac', '-b:a', '96k', '-movflags', '+faststart', str(target)], check=True)


def prepare(metadata_path, fit_path, output):
    pillow_heif.register_heif_opener()
    metadata = json.loads(metadata_path.read_text())
    originals = {}
    for item in metadata:
        name = re.sub(r'\(\d+\)(?=\.)', '', item.get('FileName', '')).lower()
        originals.setdefault(name, item)
    track = []
    with fitdecode.FitReader(fit_path) as fit:
        for frame in fit:
            if not isinstance(frame, fitdecode.FitDataMessage) or frame.name != 'record':
                continue
            fields = {f.name: f.value for f in frame.fields}
            if any(fields.get(k) is None for k in ('position_lat', 'position_long', 'timestamp', 'distance')):
                continue
            track.append((fields['timestamp'], fields['position_long'] * 180 / 2**31,
                          fields['position_lat'] * 180 / 2**31, fields['distance'] / 1000,
                          fields.get('enhanced_altitude', fields.get('altitude'))))
    media_dir = output / 'media'
    media_dir.mkdir(parents=True, exist_ok=True)
    public = []
    original_bytes = 0
    for filename, name, caption, chapter, kind, label in SPECS:
        meta = originals[filename.lower()]
        source = Path(meta['SourceFile'])
        original_bytes += source.stat().st_size
        if kind == 'video':
            captured = datetime.strptime(meta['CreationDate'], '%Y:%m:%d %H:%M:%S%z')
        else:
            captured = datetime.strptime(meta['DateTimeOriginal'] + meta['OffsetTimeOriginal'], '%Y:%m:%d %H:%M:%S%z')
        point = min(track, key=lambda p: abs((p[0] - captured).total_seconds()))
        offset = 111320 * math.hypot((meta['GPSLongitude'] - point[1]) * math.cos(math.radians(point[2])), meta['GPSLatitude'] - point[2])
        if kind == 'video':
            target = media_dir / f'{name}.mp4'
            encode_video(source, target)
            poster = media_dir / f'{name}-poster.jpg'
            subprocess.run(['ffmpeg', '-hide_banner', '-loglevel', 'error', '-y', '-ss', '2', '-i', str(target),
                '-frames:v', '1', '-q:v', '4', str(poster)], check=True)
            with Image.open(poster) as image:
                dimensions = image.size
                image.thumbnail((320, 320))
                image.save(media_dir / f'{name}-thumb.webp', 'WEBP', quality=75)
            # Re-save to remove encoder metadata as well as GPS/location tags.
            with Image.open(poster) as image:
                image.convert('RGB').save(poster, 'JPEG', quality=80, optimize=True)
            src = f'media/{name}.mp4'
            info = {'poster': f'media/{name}-poster.jpg', 'width': dimensions[0], 'height': dimensions[1], 'durationSeconds': round(meta['Duration'], 2)}
        else:
            with Image.open(source) as original:
                image = ImageOps.exif_transpose(original).convert('RGB')
                widths = [960, 1600, 2400, 3200] if kind == 'cover' else [480, 960, 1600]
                for width in widths:
                    resized = image.resize((width, round(image.height * width / image.width)), Image.Resampling.LANCZOS)
                    resized.save(media_dir / f'{name}-{width}.webp', 'WEBP', quality=82, method=6)
                thumb = image.copy()
                thumb.thumbnail((320, 320))
                thumb.save(media_dir / f'{name}-thumb.webp', 'WEBP', quality=75)
                default_width = 2400 if kind == 'cover' else 960
                info = {'width': default_width, 'height': round(image.height * default_width / image.width),
                        'srcset': ', '.join(f'media/{name}-{w}.webp {w}w' for w in widths)}
            src = f'media/{name}-{default_width}.webp'
        public.append({'id': name, 'type': kind, 'src': src, 'thumbnail': f'media/{name}-thumb.webp',
                       'caption': caption, 'chapter': chapter, 'mapLabel': label,
                       'capturedLocal': captured.isoformat(), 'time': captured.strftime('%H:%M'),
                       'coordinate': [round(point[1], 6), round(point[2], 6)],
                       'distanceKm': round(point[3], 2), 'elevationM': round(point[4]),
                       'positionMethod': 'capture time' if offset > 150 else 'capture time and GPS',
                       'cameraGpsOffsetM': round(offset), 'recordingTimeOffsetSeconds': round(abs((point[0] - captured).total_seconds())),
                       **info})
        print(name, captured.strftime('%H:%M'), f'{point[3]:.2f} km', f'GPS difference {offset:.0f} m', flush=True)
    (output / 'media.json').write_text(json.dumps(public, indent=2) + '\n')
    output_bytes = sum(p.stat().st_size for p in media_dir.iterdir())
    print(f'{original_bytes / 1024**2:.1f} MB originals → {output_bytes / 1024**2:.1f} MB across ALL responsive variants, videos, posters and thumbnails')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--metadata', type=Path, required=True)
    parser.add_argument('--fit', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    prepare(args.metadata, args.fit, args.output)
