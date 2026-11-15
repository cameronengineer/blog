#!/usr/bin/env python3
"""Compile content/posts/*.md into a self-contained static site in public/."""
from __future__ import annotations

import argparse
from collections import Counter
from dataclasses import dataclass
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
import os
from pathlib import Path
import re
import shutil
from string import Template
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

import markdown
from markdown.extensions.toc import slugify
import yaml

ROOT = Path(__file__).resolve().parents[1]
DESCRIPTION = "Notes on engineering, languages and flying. A personal notebook by Cameron Mitchell."
TOPICS = {"languages": "Languages", "engineering": "Engineering", "flying": "Flying", "adventure": "Adventure"}


@dataclass
class Post:
    slug: str
    title: str
    description: str
    date: date
    updated: date
    tags: list[str]
    body: str
    toc: str
    minutes: int
    cover: dict | None = None

    @property
    def url(self):
        return f"/posts/{self.slug}/"


def read_posts():
    posts = []
    for path in sorted((ROOT / "content/posts").glob("*.md")):
        raw = path.read_text(encoding="utf-8")
        match = re.match(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|$)(.*)\Z", raw, re.S)
        if not match:
            raise ValueError(f"{path.name}: expected YAML front matter between --- lines")
        meta = yaml.safe_load(match[1])
        if meta.get("draft", False):
            continue
        published = date.fromisoformat(str(meta["date"])[:10])
        updated = date.fromisoformat(str(meta.get("lastmod", published))[:10])
        title = str(meta["title"])
        tags = meta.get("tags", [])
        if not isinstance(tags, list) or not all(isinstance(t, str) for t in tags):
            raise ValueError(f"{path.name}: tags must be a list of strings")
        md = markdown.Markdown(extensions=["tables", "fenced_code", "toc", "sane_lists"],
                               extension_configs={"toc": {"permalink": False}})
        body = md.convert(match[2])
        body = re.sub(r"<table>(.*?)</table>", r'<div class="table-scroll" tabindex="0" role="region" aria-label="Scrollable data table"><table>\1</table></div>', body, flags=re.S)
        # Keep author-written HTML (including the Moorabbin map) and make embeds accessible.
        body = body.replace('name="iframe"', 'name="iframe" title="Moorabbin reporting points map" loading="lazy"')
        minutes = max(1, round(len(match[2].split()) / 220))
        cover = meta.get("cover")
        if cover is not None and (not isinstance(cover, dict) or not all(k in cover for k in ("src", "alt", "width", "height"))):
            raise ValueError(f"{path.name}: cover needs src, alt, width and height")
        posts.append(Post(path.stem, title, str(meta.get("description", "")), published,
                          updated, tags, body, md.toc if md.toc_tokens else "", minutes, cover))
    return sorted(posts, key=lambda p: (p.date, p.slug), reverse=True)


def tag_url(tag):
    return f"/tags/{slugify(tag, '-')}/"


def tag_links(tags):
    return '<div class="tags">' + "".join(
        f'<a href="{tag_url(t)}">{escape(t.capitalize())}</a>' for t in tags) + '</div>'


def date_label(value):
    return f"{value.day} {value:%b %Y}"


def note_list(posts, latest=False):
    rows = []
    for i, p in enumerate(posts):
        category = next((TOPICS[t] for t in TOPICS if t in p.tags), "Notes")
        label = "Latest · " + category if latest and i == 0 else category
        rows.append(f'''<article class="note" data-note>
          <div class="note-meta"><span class="eyebrow">{escape(label)}</span><time datetime="{p.date}">{date_label(p.date)}</time></div>
          <div><h3><a href="{p.url}">{escape(p.title)}</a></h3><p>{escape(p.description)}</p>{tag_links(p.tags)}</div>
          <a class="arrow" href="{p.url}" aria-label="Read {escape(p.title, quote=True)}">↗</a>
        </article>''')
    return '<div class="note-list">' + "".join(rows) + '</div>'


def build(output: Path, base_url: str):
    parsed = urlparse(base_url)
    if parsed.scheme not in ("https", "http") or not parsed.netloc or parsed.path not in ("", "/") or parsed.query or parsed.fragment:
        raise ValueError("Base URL must be an absolute http(s) address at the domain root")
    base_url = base_url.rstrip("/")
    posts = read_posts()
    topic_navigation = ''.join(
        f'<a href="{tag_url(tag)}">{name}</a>'
        for tag, name in TOPICS.items() if any(tag in p.tags for p in posts))
    template = Template((ROOT / "templates/base.html").read_text())
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    shutil.copytree(ROOT / "static", output, dirs_exist_ok=True)
    shutil.copytree(ROOT / "assets", output / "assets")
    pages = []

    def write(path, text):
        destination = output / path
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(text, encoding="utf-8")

    def page(url, title, description, content, article=False, image_url=None):
        write(url.lstrip("/") + "index.html", template.substitute(
            title=escape(title + " · Cameron's notes", quote=True),
            description=escape(description, quote=True), canonical=escape(base_url + url, quote=True),
            og_type="article" if article else "website", content=content,
            topic_navigation=topic_navigation,
            social_image=f'<meta property="og:image" content="{escape(image_url, quote=True)}">' if image_url else ""))
        pages.append(url)

    topic_counts = Counter(t for p in posts for t in p.tags)
    search = '''<div class="search" data-search hidden><label for="note-search">Find a note</label><input id="note-search" type="search" placeholder="A word or topic…" autocomplete="off" aria-controls="note-results"></div>'''
    home = f'''<section class="notebook" id="notebook" aria-labelledby="notebook-title"><div class="section-head"><h1 id="notebook-title">Notes</h1>{search}</div>
      <div id="note-results">{note_list(posts, latest=True)}</div><p class="search-status" data-search-status role="status">{len(posts)} notes · Most recent first</p></section>'''
    page("/", "The notebook", DESCRIPTION, home)
    page("/posts/", "All notes", DESCRIPTION,
         '<div class="topic-head"><p class="eyebrow">The notebook</p><h1>All notes.</h1><p>Most recent first. Follow a curiosity.</p></div><section class="notebook">' + note_list(posts) + '</section>')
    for p in posts:
        cover = ""
        if p.cover:
            c = p.cover
            cover = f'''<figure class="article-cover"><a href="{escape(str(c['src']), quote=True)}"><img src="{escape(str(c['src']), quote=True)}" srcset="{escape(c.get('srcset', ''), quote=True)}" sizes="(max-width: 1144px) calc(100vw - 64px), 1080px" width="{int(c['width'])}" height="{int(c['height'])}" alt="{escape(c['alt'], quote=True)}" fetchpriority="high" decoding="async"></a><figcaption>{escape(c.get('caption', ''))}</figcaption></figure>'''
        toc = f'<details class="contents" open><summary>In this note</summary>{p.toc}</details>' if p.toc else ''
        category = next((TOPICS[t] for t in TOPICS if t in p.tags), "Notes")
        modified = f'<span>Updated {date_label(p.updated)}</span>' if p.updated != p.date else ''
        content = f'''<div class="breadcrumb"><a href="/">The notebook</a> <span aria-hidden="true"> / </span> {escape(category)}</div>
          <article><header class="article-head"><p class="eyebrow">{escape(category)}</p><h1>{escape(p.title)}</h1>
          <p class="dek">{escape(p.description)}</p><div class="article-meta"><span>Cameron Mitchell</span><time datetime="{p.date}">{date_label(p.date)}</time><span>{p.minutes} min read</span>{modified}</div>{tag_links(p.tags)}</header>
          {cover}<div class="article-layout"><div class="prose">{p.body}<div class="article-end"><a href="/#notebook">← Back to the notebook</a></div></div>{toc}</div></article>'''
        page(p.url, p.title, p.description, content, article=True,
             image_url=base_url + p.url + p.cover['src'] if p.cover else None)
    topic_items = ''.join(f'<li><a href="{tag_url(t)}">{escape(t.capitalize())} <span class="count">{topic_counts[t]:02}</span></a></li>' for t in sorted(topic_counts))
    page("/tags/", "Topics", "Browse the notebook by topic.", f'<div class="topic-head"><p class="eyebrow">The notebook</p><h1>Follow a topic.</h1><ul class="topic-list">{topic_items}</ul></div>')
    for tag in sorted(topic_counts):
        selected = [p for p in posts if tag in p.tags]
        page(tag_url(tag), tag.capitalize(), f"Notes about {tag} by Cameron Mitchell.",
             f'<div class="breadcrumb"><a href="/">The notebook</a> / <a href="/tags/">Topics</a></div><div class="topic-head"><p class="eyebrow">Filed under</p><h1>{escape(tag.capitalize())}.</h1><p>{len(selected)} {"note" if len(selected) == 1 else "notes"} from the notebook.</p></div><section class="notebook">{note_list(selected)}</section>')
    page("/categories/", "Topics", "Browse the notebook by topic.", f'<div class="topic-head"><h1>Follow a topic.</h1><ul class="topic-list">{topic_items}</ul></div>')
    error = template.substitute(title="Page not found · Cameron's notes", description="This page isn't in the notebook.",
         canonical=base_url + '/404.html', og_type="website", topic_navigation=topic_navigation, social_image="", content='<div class="topic-head"><p class="eyebrow">404 · A wrong turn</p><h1>Not in this notebook.</h1><p>This page may have moved, or the address may be mistyped.</p><p><a href="/">Back to the notebook →</a></p></div>')
    write("404.html", error)
    # Preserve Hugo's first-page aliases as normal HTML redirects.
    for alias, target in (("page/1/index.html", "/"), ("posts/page/1/index.html", "/posts/")):
        write(alias, f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Redirecting</title><meta http-equiv="refresh" content="0;url={target}"><link rel="canonical" href="{base_url}{target}"></head><body><a href="{target}">Continue to the notebook</a></body></html>')
    def feed(selected, path):
        rss = ET.Element("rss", version="2.0")
        channel = ET.SubElement(rss, "channel")
        for name, value in (("title", "Cameron's notes"), ("link", base_url + "/"), ("description", DESCRIPTION), ("language", "en-au")):
            ET.SubElement(channel, name).text = value
        for p in selected:
            item = ET.SubElement(channel, "item")
            for name, value in (("title", p.title), ("link", base_url + p.url), ("guid", base_url + p.url),
                                ("description", p.description), ("pubDate", format_datetime(datetime.combine(p.date, datetime.min.time(), tzinfo=timezone.utc)))):
                ET.SubElement(item, name).text = value
            for tag in p.tags:
                ET.SubElement(item, "category").text = tag
        write(path, ET.tostring(rss, encoding="unicode", xml_declaration=True))
    feed(posts, "index.xml")
    feed(posts, "posts/index.xml")
    for tag in topic_counts:
        feed([p for p in posts if tag in p.tags], tag_url(tag).lstrip("/") + "index.xml")
    sitemap = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    for url in pages:
        item = ET.SubElement(sitemap, "url")
        ET.SubElement(item, "loc").text = base_url + url
        post = next((p for p in posts if p.url == url), None)
        if post:
            ET.SubElement(item, "lastmod").text = str(post.updated)
    write("sitemap.xml", ET.tostring(sitemap, encoding="unicode", xml_declaration=True))
    write("robots.txt", f"User-agent: *\nAllow: /\nSitemap: {base_url}/sitemap.xml\n")
    print(f"Built {len(posts)} posts and {len(pages)} pages → {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default=os.environ.get("SITE_URL") or os.environ.get("RENDER_EXTERNAL_URL") or "https://blog.cameronengineer.com")
    args = parser.parse_args()
    build(ROOT / "public", args.base_url)
