# Cameron's notes

A small Markdown-to-HTML blog. Python compiles the posts; Render serves the plain
HTML, CSS, images and a small optional search script. No Hugo, theme framework,
Node.js or server application.

## Build and preview

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python scripts/build.py
.venv/bin/python -m http.server 8000 --directory public
```

Open http://localhost:8000. The script requires Python 3.10 or newer and two
libraries: Python-Markdown and PyYAML. It recreates `public/` on every build.

## Write a note

Add a Markdown file in `content/posts/`, for example `26-11-15-a-new-note.md`:

```yaml
---
title: A new note
description: A short description for the index and link previews.
date: 2026-11-15
lastmod: 2026-11-15
draft: false
tags:
  - engineering
---
```

Write the post below the front matter. Tables, fenced code, normal Markdown and
inline HTML are supported. Headings get anchors and an automatic contents list.
Drafts stay out of the site, topic pages, feed and sitemap.

The filename becomes `/posts/26-11-15-a-new-note/`. Put images and downloads in
`static/posts/26-11-15-a-new-note/` and link them with relative paths in Markdown.
Files in `static/` are copied unchanged, including the existing interactive map.

Edit `templates/base.html` for the shared page layout, `assets/style.css` for the
visual design, and `scripts/build.py` for the index and article structure.

## Deploy

Push to `main`. Render runs `bash scripts/render-build.sh` and publishes `public/`.
The site is https://blog.cameronengineer.com/ (also available at
https://blog-kcnz.onrender.com/); its configuration is recorded in
`render.yaml`. GitHub Pages is no longer used for builds.

`SITE_URL=https://blog.cameronengineer.com` sets canonical URLs, RSS and the sitemap
on Render. If unset, builds fall back to `RENDER_EXTERNAL_URL`, then the custom domain.
For a local override, use `scripts/build.py --base-url https://example.com`.

## Checks

```sh
.venv/bin/python -m unittest discover -s tests
```

## Recorded adventures

The Marmolada post has a standalone route viewer in
`static/posts/26-11-16-marmolada/`. MapLibre GL JS 5.6.1 is vendored in
`assets/vendor/` with its licence. The map fetches OpenStreetMap basemap tiles
and Mapterhorn elevation tiles as needed. Route and elevation SVGs work without
those services or JavaScript. The viewer does not require an API key.

To import another FIT recording (an optional authoring tool, separate from the
site build):

```sh
.venv/bin/pip install fitdecode==0.11.0
.venv/bin/python scripts/import_hike.py /path/to/activity.fit static/posts/post-slug
```

This exports GPS positions, recorded elevation and distance, a small activity
summary, and the fallback SVGs. It excludes health metrics and device details.
Keep the original FIT file outside the public site. Write the corresponding
Markdown post separately; the importer does not invent trip details.
