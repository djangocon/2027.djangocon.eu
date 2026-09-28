"""What the served pages cost to load: asset bundles, images, caching."""

import re
from pathlib import Path

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


class TestTrimmedBootstrap:
    """_bootstrap.scss compiles only the utilities the markup uses."""

    UTILITY = re.compile(
        r"(?:d|flex|justify-content|align-(?:items|self|content)|gap|row-gap|column-gap|order"
        r"|[mp][tbsexy]?|text|w|h|mw|mh|vw|vh|fw|fs|fst|lh|position|top|bottom|start|end"
        r"|bg|border|rounded|shadow|opacity|overflow|float|z|user-select|pe)-[a-z0-9-]+"
    )

    def test_every_utility_class_used_is_compiled(self):
        css = Path(finders.find("css/project.min.css")).read_text(encoding="utf-8")
        sources = [*Path("djangocon/templates").rglob("*.html"), *content.content_dir().rglob("*.md")]
        missing = set()
        for path in sources:
            for attr in re.findall(r'class="([^"]*)"', path.read_text(encoding="utf-8")):
                for token in attr.split():
                    if self.UTILITY.fullmatch(token) and not re.search(rf"\.{re.escape(token)}[^a-zA-Z0-9_-]", css):
                        missing.add(f"{token} ({path.name})")
        assert not missing, f"add the utility to $utilities in _bootstrap.scss: {sorted(missing)}"


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


class TestHeroImage:
    """The mountain silhouette is the home page's LCP element."""

    def _hero(self, client: Client) -> str:
        html = client.get("/").content.decode()
        return re.search(r"<img[^>]*hero-mountain-img[^>]*>", html, re.S).group(0)

    def test_fetched_at_high_priority(self, client: Client):
        tag = self._hero(client)
        assert 'fetchpriority="high"' in tag
        assert "loading=" not in tag, "the LCP image must never be lazy-loaded"

    def test_reserves_its_space(self, client: Client):
        tag = self._hero(client)
        assert 'width="' in tag
        assert 'height="' in tag

    def test_offers_narrower_copies(self, client: Client):
        assert "1200w" in self._hero(client)


class TestPastEditions:
    """The photo strip sits below the fold on the home page."""

    def test_photos_are_lazy_sized_and_responsive(self, client: Client):
        html = client.get("/").content.decode()
        tags = re.findall(r'<a class="edition".*?(<img.*?>)', html, re.S)
        assert tags
        for tag in tags:
            assert 'loading="lazy"' in tag
            assert 'width="' in tag
            assert 'height="' in tag
            assert "srcset=" in tag
            assert ".png" not in tag


class TestFonts:
    def test_no_third_party_font_requests(self):
        """Google Fonts would send every visitor's IP to Google before any consent."""
        css = Path(finders.find("css/project.min.css")).read_text(encoding="utf-8")
        assert "fonts.googleapis.com" not in css
        assert "fonts.gstatic.com" not in css

    def test_every_font_face_file_exists(self):
        css = Path(finders.find("css/project.min.css")).read_text(encoding="utf-8")
        files = re.findall(r"url\(\.\./fonts/([^)]+)\)", css)
        assert files
        for name in files:
            assert finders.find(f"fonts/{name}"), f"missing font file {name}"

    def test_preloaded_fonts_are_declared_in_the_css(self, client: Client):
        """A preload nothing uses is a wasted download (and a console warning)."""
        css = Path(finders.find("css/project.min.css")).read_text(encoding="utf-8")
        html = client.get("/").content.decode()
        preloads = re.findall(r'<link rel="preload"\s+href="/static/fonts/([^"]+)"', html)
        assert preloads
        for name in preloads:
            assert f"../fonts/{name}" in css
