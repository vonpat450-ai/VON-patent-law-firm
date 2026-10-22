"""Checks for search-facing HTML produced by the column build."""

from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import unittest
from xml.etree import ElementTree


ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"
BASE = "https://vonpatglobalpt.net"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []
        self.images = []
        self.title = ""
        self.description = []
        self.canonical = []
        self.schemas = []
        self._capture = None

    def handle_starttag(self, tag, attrs):
        data = dict(attrs)
        self.tags.append(tag)
        if tag == "img":
            self.images.append(data)
        if tag == "title":
            self._capture = "title"
        if tag == "meta" and data.get("name") == "description":
            self.description.append(data.get("content", ""))
        if tag == "link" and data.get("rel") == "canonical":
            self.canonical.append(data.get("href", ""))
        if tag == "script" and data.get("type") == "application/ld+json":
            self._capture = "schema"

    def handle_endtag(self, tag):
        if tag in {"title", "script"}:
            self._capture = None

    def handle_data(self, data):
        if self._capture == "title":
            self.title += data
        elif self._capture == "schema":
            self.schemas.append(json.loads(data))


class SeoPageTests(unittest.TestCase):
    def test_public_pages_have_indexable_static_content_and_unique_metadata(self):
        pages = sorted(DIST.glob("*.html"))
        pages = [page for page in pages if page.name not in {"404.html", "search.html"}]
        self.assertGreaterEqual(len(pages), 7)
        titles = set()
        descriptions = set()
        for page in pages:
            with self.subTest(page=page.name):
                html = page.read_text(encoding="utf-8")
                parsed = PageParser()
                parsed.feed(html)
                canonical = BASE + ("/" if page.stem == "index" else f"/{page.stem}")
                self.assertEqual(parsed.tags.count("main"), 1)
                self.assertEqual(parsed.tags.count("h1"), 1)
                self.assertIn("<!--STATIC_RENDER_START-->", html)
                self.assertIn("<!--STATIC_RENDER_END-->", html)
                self.assertEqual(parsed.canonical, [canonical])
                self.assertEqual(len(parsed.description), 1)
                self.assertGreater(len(parsed.description[0]), 40)
                self.assertNotIn(parsed.title, titles)
                self.assertNotIn(parsed.description[0], descriptions)
                self.assertTrue(parsed.schemas)
                self.assertTrue(all("alt" in image for image in parsed.images))
                titles.add(parsed.title)
                descriptions.add(parsed.description[0])

    def test_canonicals_match_sitemap_and_future_articles_are_not_listed(self):
        sitemap = ElementTree.parse(DIST / "sitemap.xml")
        namespace = {"s": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        locations = {node.text for node in sitemap.findall("s:url/s:loc", namespace)}
        for page in DIST.glob("*.html"):
            if page.name in {"404.html", "search.html"}:
                continue
            parsed = PageParser()
            parsed.feed(page.read_text(encoding="utf-8"))
            self.assertIn(parsed.canonical[0], locations)

        schedule = json.loads((DIST / "publication-schedule.json").read_text(encoding="utf-8"))
        now = datetime.now(timezone.utc)
        for entry in schedule["articles"]:
            if datetime.fromisoformat(entry["publish_at"]).astimezone(timezone.utc) > now:
                for listing in ("index.html", "knowledge.html"):
                    with self.subTest(future=entry["href"], listing=listing):
                        self.assertNotIn(entry["href"], (DIST / listing).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
