"""Verify search metadata against rendered pages and real public assets."""
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlparse
import xml.etree.ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import build


class SearchMetadata(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.meta = {}
        self.canonical = None
        self.graphs = []
        self.script = None
        self.h1_count = 0
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'meta':
            self.meta[attrs.get('name', attrs.get('property'))] = attrs.get('content')
        elif tag == 'link' and attrs.get('rel') == 'canonical':
            self.canonical = attrs['href']
        elif tag == 'script' and attrs.get('type') == 'application/ld+json':
            self.script = ''
        elif tag == 'h1':
            self.h1_count += 1

    def handle_data(self, data):
        if self.script is not None:
            self.script += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.script is not None:
            self.graphs.append(json.loads(self.script))
            self.script = None


class SearchTests(unittest.TestCase):
    def test_article_metadata_sitemap_and_draft_isolation(self):
        base = 'https://example.com'
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / 'site'
            build.build(out, base)
            sitemap = ET.parse(out / 'sitemap.xml')
            ns = {'s': 'http://www.sitemaps.org/schemas/sitemap/0.9', 'image': 'http://www.google.com/schemas/sitemap-image/1.1'}
            indexed = {n.findtext('s:loc', namespaces=ns) for n in sitemap.findall('s:url', ns)}
            self.assertNotIn(base + '/categories/', indexed)
            for post in build.read_posts():
                html = (out / post.url.strip('/') / 'index.html').read_text()
                metadata = SearchMetadata(html)
                self.assertEqual(metadata.canonical, base + post.url)
                self.assertEqual(metadata.h1_count, 1)
                if post.draft:
                    self.assertEqual(metadata.meta['robots'], 'noindex')
                    self.assertEqual(metadata.graphs, [])
                    self.assertNotIn(base + post.url, indexed)
                    continue
                self.assertIn(base + post.url, indexed)
                self.assertEqual(metadata.meta['robots'], 'max-image-preview:large')
                self.assertEqual(metadata.meta['og:url'], metadata.canonical)
                nodes = metadata.graphs[0]['@graph']
                article = next(n for n in nodes if n['@type'] == 'BlogPosting')
                person = next(n for n in nodes if n['@type'] == 'Person')
                self.assertEqual(article['headline'], post.title)
                self.assertEqual(article['description'], post.description)
                self.assertEqual(article['datePublished'], str(post.date))
                self.assertEqual(article['dateModified'], str(post.updated))
                self.assertEqual(article['author']['@id'], person['@id'])
                self.assertEqual(person['name'], 'Cameron Mitchell')
                crumbs = next(n for n in nodes if n['@type'] == 'BreadcrumbList')['itemListElement']
                self.assertEqual([c['position'] for c in crumbs], list(range(1, len(crumbs) + 1)))
                self.assertEqual(crumbs[-1]['item'], base + post.url)
                for crumb in crumbs:
                    self.assertIn(crumb['item'], indexed)
                if article.get('image'):
                    self.assertEqual(metadata.meta['og:image'], article['image'][0])
                    self.assertEqual(metadata.meta['twitter:card'], 'summary_large_image')
                for url in article.get('image', []):
                    self.assertTrue((out / unquote(urlparse(url).path).lstrip('/')).is_file())
            for image in sitemap.findall('.//image:loc', ns):
                self.assertTrue(image.text.startswith(base + '/'))
                self.assertTrue((out / unquote(urlparse(image.text).path).lstrip('/')).is_file())
            canonical_alias = SearchMetadata((out / 'categories/index.html').read_text())
            self.assertEqual(canonical_alias.canonical, base + '/tags/')
            italian = (out / 'posts/26-11-15-italian-flashcards/index.html').read_text()
            self.assertIn('Related notes', italian)
            self.assertIn('/posts/25-08-17-super-beginner-words/', italian)
            self.assertNotIn('/posts/24-11-17-ansible-aws-ssm/', italian)

    def test_structured_data_cannot_close_its_script_tag(self):
        title = '</script><script>alert("example")</script> & notes'
        html = build.json_ld([{'@type': 'BlogPosting', 'headline': title}])
        self.assertEqual(html.count('</script>'), 1)
        self.assertIn('\\u003c/script>', html)
        self.assertEqual(SearchMetadata(html).graphs[0]['@graph'][0]['headline'], title)


if __name__ == '__main__':
    unittest.main()
