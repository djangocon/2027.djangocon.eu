"""What the served pages cost to load: asset bundles, images, caching."""

import re

from django.contrib.staticfiles import finders
from django.test import Client

from djangocon.site.utils import content


class TestAssetBundles:
    def test_pages_load_the_minified_bundles(self, client: Client):
        """gulp builds both flavours; only the .min ones should reach visitors."""
        html = client.get("/").content.decode()
        for href in re.findall(r'(?:href|src)="([^"]+\.(?:css|js))"', html):
            if href.startswith("/static/"):
                assert ".min." in href, f"unminified asset served: {href}"


class TestContentStaticUrls:
    """Hand-written /static/ URLs in content files go through the storage."""

    def test_rewritten_to_the_storage_url(self, monkeypatch):
        monkeypatch.setattr(content, "static", lambda path: f"/static/{path.replace('.', '.abc123.', 1)}")
        html = (
            '<img src="/static/images/a.png" srcset="/static/images/a.png 1x, /static/images/b.png 2x">'
            '<a href="/static/docs/x.pdf">x</a>'
        )
        assert content.resolve_static_urls(html) == (
            '<img src="/static/images/a.abc123.png" srcset="/static/images/a.abc123.png 1x, '
            '/static/images/b.abc123.png 2x"><a href="/static/docs/x.abc123.pdf">x</a>'
        )

    def test_missing_file_is_left_alone(self, monkeypatch):
        def strict(path):
            raise ValueError(path)

        monkeypatch.setattr(content, "static", strict)
        assert content.resolve_static_urls('<img src="/static/nope.png">') == '<img src="/static/nope.png">'

    def test_every_referenced_file_exists(self):
        """A typo would otherwise ship a broken image and an uncached URL."""
        for path in content.content_dir().rglob("*.md"):
            for ref in re.findall(r"/static/([^\s\"'(),?#]+)", path.read_text(encoding="utf-8")):
                assert finders.find(ref), f"{path.name} references missing static file {ref}"
