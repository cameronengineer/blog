"""Check publishing behavior against a small, separate notebook."""
from html.parser import HTMLParser
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get('id'):
            self.ids.add(attrs['id'])
        for key in ('src', 'href'):
            if attrs.get(key):
                self.links.append(attrs[key])


class PublishingTests(unittest.TestCase):
    def test_published_posts_assets_feeds_and_drafts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'content/posts').mkdir(parents=True)
            (root / 'static/posts/26-01-01-first').mkdir(parents=True)
            (root / 'static/posts/26-01-01-first/data.txt').write_text('original attachment')
            shutil.copytree(build.ROOT / 'templates', root / 'templates')
            shutil.copytree(build.ROOT / 'assets', root / 'assets')
            (root / 'content/posts/26-01-01-first.md').write_text('''---
title: 'A <small> note & example'
description: 'Testing "quotes" & links'
date: 2026-01-01
tags: [engineering]
---
## A heading

[Attachment](data.txt)

| One | Two |
| --- | --- |
| A | B |

```python
print("hello")
```
''')
            (root / 'content/posts/26-01-02-second.md').write_text('''---
title: Second
date: 2026-01-02
tags: [languages]
---
A newer note.
''')
            (root / 'content/posts/26-01-03-secret.md').write_text('''---
title: Secret draft
date: 2026-01-03
draft: true
tags: [secret]
---
Draft preview body.
''')
            out = root / 'public'
            with patch.object(build, 'ROOT', root):
                build.build(out, 'https://example.com')
                (out / 'stale.html').write_text('obsolete')
                build.build(out, 'https://example.com')
            self.assertFalse((out / 'stale.html').exists())
            draft_path = out / 'posts/26-01-03-secret/index.html'
            draft_html = draft_path.read_text()
            self.assertIn('Draft preview body.', draft_html)
            self.assertIn('<meta name="robots" content="noindex">', draft_html)
            self.assertNotIn('href="/tags/secret/"', draft_html)
            self.assertFalse((out / 'tags/secret').exists())
            for path in out.rglob('*'):
                if path.suffix in ('.xml', '.html') and path != draft_path:
                    self.assertNotIn('Secret draft', path.read_text())
            html = (out / 'posts/26-01-01-first/index.html').read_text()
            self.assertIn('A &lt;small&gt; note &amp; example', html)
            self.assertIn('id="a-heading"', html)
            self.assertIn('href="#a-heading"', html)
            self.assertIn('<table>', html)
            self.assertIn('<code class="language-python">', html)
            self.assertEqual((out / 'posts/26-01-01-first/data.txt').read_text(), 'original attachment')
            items = ET.parse(out / 'index.xml').findall('./channel/item')
            self.assertEqual([i.findtext('title') for i in items], ['Second', 'A <small> note & example'])
            self.assertEqual(len(ET.parse(out / 'tags/engineering/index.xml').findall('./channel/item')), 1)
            self.assertIn('https://example.com/posts/26-01-01-first/', (out / 'sitemap.xml').read_text())
            self.assertNotIn('/posts/26-01-03-secret/', (out / 'sitemap.xml').read_text())
            self.assertNotIn('content="noindex"', html)
            # Publishing a preview removes noindex and makes it discoverable.
            draft_source = root / 'content/posts/26-01-03-secret.md'
            draft_source.write_text(draft_source.read_text().replace('draft: true', 'draft: false'))
            with patch.object(build, 'ROOT', root):
                build.build(out, 'https://example.com')
            self.assertNotIn('content="noindex"', draft_path.read_text())
            self.assertIn('Secret draft', (out / 'index.html').read_text())
            self.assertIn('Secret draft', (out / 'index.xml').read_text())
            self.assertIn('/posts/26-01-03-secret/', (out / 'sitemap.xml').read_text())
            self.assertTrue((out / 'tags/secret/index.html').exists())

    def test_real_site_has_no_broken_internal_links_or_fragments(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = (Path(tmp) / 'site').resolve()
            build.build(out, 'https://example.com')
            documents = {}
            for path in out.rglob('*.html'):
                parser = Links()
                parser.feed(path.read_text())
                documents[path.resolve()] = parser
            for source, document in documents.items():
                for link in document.links:
                    url = urlparse(link)
                    if url.scheme or url.netloc:
                        continue
                    if not url.path:
                        target = source
                    else:
                        target = out / unquote(url.path.lstrip('/')) if url.path.startswith('/') else source.parent / unquote(url.path)
                        if target.is_dir():
                            target /= 'index.html'
                    with self.subTest(source=source.relative_to(out), link=link):
                        self.assertTrue(target.exists(), f'Missing {target}')
                        if url.fragment and target.resolve() in documents:
                            self.assertIn(unquote(url.fragment), documents[target.resolve()].ids)

    def test_invalid_base_url_rejected_before_output_changes(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'output'
            for url in ('example.com', 'https://example.com/path', 'javascript:alert(1)'):
                with self.subTest(url=url), self.assertRaises(ValueError):
                    build.build(path, url)
            self.assertFalse(path.exists())


if __name__ == '__main__':
    unittest.main()
