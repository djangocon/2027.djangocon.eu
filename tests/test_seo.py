"""robots.txt, sitemap.xml, the consent-gated analytics tag, and the served markup."""

import re
from http import HTTPStatus

from django.test import Client

from djangocon.site.sitemaps import ContentSitemap


def _locs(body: str) -> list[str]:
    return re.findall(r"<loc>(.*?)</loc>", body)


class TestRobotsTxt:
    def test_served_as_plain_text(self, client: Client):
        response = client.get("/robots.txt")
        assert response.status_code == HTTPStatus.OK
        assert response["Content-Type"].startswith("text/plain")

    def test_allows_crawling_and_points_at_the_sitemap(self, client: Client):
        body = client.get("/robots.txt").content.decode()
        assert "User-agent: *" in body
        assert "Allow: /" in body
        # The Sitemap line has to be an absolute URL or crawlers ignore it.
        assert "Sitemap: http://testserver/sitemap.xml" in body

    def test_is_a_single_record(self, client: Client):
        """A blank line starts a new record, which would orphan the Disallow rules."""
        body = client.get("/robots.txt").content.decode()
        directives, _, sitemap = body.partition("\n\n")
        assert "" not in directives.split("\n")
        assert sitemap.startswith("Sitemap:")


class TestSitemap:
    def test_served_as_xml(self, client: Client):
        response = client.get("/sitemap.xml")
        assert response.status_code == HTTPStatus.OK
        assert "xml" in response["Content-Type"]

    def test_lists_the_content_pages(self, client: Client):
        locs = _locs(client.get("/sitemap.xml").content.decode())
        assert "https://testserver/" in locs
        assert "https://testserver/talks/cfp/" in locs
        assert "https://testserver/information/venue/" in locs
        assert "https://testserver/sponsors/sponsors/" in locs

    def test_excludes_the_home_redirect(self, client: Client):
        """/home/ is a permanent redirect to /; only the canonical URL belongs here."""
        assert "https://testserver/home/" not in _locs(client.get("/sitemap.xml").content.decode())

    def test_every_url_is_actually_served(self, client: Client):
        """A sitemap that advertises a 404 is worse than no sitemap."""
        for loc in _locs(client.get("/sitemap.xml").content.decode()):
            path = loc.replace("https://testserver", "")
            assert client.get(path).status_code == HTTPStatus.OK, f"{path} is in the sitemap but does not render"

    def test_home_page_ranks_highest(self, client: Client):
        body = client.get("/sitemap.xml").content.decode()
        home = re.search(
            r"<loc>https://testserver/</loc>"
            r"<lastmod>[^<]*</lastmod><changefreq>[^<]*</changefreq>"
            r"<priority>([\d.]+)</priority>",
            body,
        )
        assert home is not None
        assert float(home.group(1)) == 1.0


class TestAnalytics:
    def test_absent_when_no_measurement_id_is_configured(self, client: Client, settings):
        """Local development and CI must not ship a tag or a banner."""
        settings.GA4_MEASUREMENT_ID = ""
        html = client.get("/").content.decode()
        assert "cookie-banner" not in html
        assert "googletagmanager" not in html

    def test_banner_shown_when_configured(self, client: Client, settings):
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        html = client.get("/").content.decode()
        assert "cookie-banner" in html
        assert "cookie-accept" in html
        assert "cookie-decline" in html

    def test_tag_is_not_loaded_before_consent(self, client: Client, settings):
        """gtag.js must only be injected by the accept handler, never by the markup."""
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        html = client.get("/").content.decode()
        assert 'src="https://www.googletagmanager.com' not in html

    def test_tag_setup_is_in_the_head(self, client: Client, settings):
        """Google's gtag.js install guide puts the tag in <head>."""
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        html = client.get("/").content.decode()
        head = html[: html.index("</head>")]
        assert "window.djcConsent" in head
        # escapejs encodes the hyphen, which JS decodes back to "G-TESTID1234".
        assert "G\\u002DTESTID1234" in head

    def test_banner_markup_is_in_the_body(self, client: Client, settings):
        """A <div> cannot live in <head>, so the UI half goes after it."""
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        html = client.get("/").content.decode()
        assert html.index('id="cookie-banner"') > html.index("</head>")

    def test_inline_scripts_carry_no_comments(self, client: Client, settings):
        """Explanatory comments belong in the template, not in what the browser is served.

        {% comment %} blocks are stripped server-side; a // comment inside the
        <script> is not, and shows up in view-source.
        """
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        html = client.get("/").content.decode()
        for block in re.findall(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", html, re.S):
            for line in block.splitlines():
                assert not line.strip().startswith(("//", "/*")), f"comment served to browser: {line.strip()}"

    def test_no_noscript_fallback(self, client: Client, settings):
        """That is a GTM pattern; GA4 measures only in JS, so it would be dead markup."""
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        assert "<noscript" not in client.get("/").content.decode()

    def test_banner_links_to_the_privacy_guide(self, client: Client, settings):
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        html = client.get("/").content.decode()
        assert "/conduct/privacy_guide/" in html


class TestServedMarkup:
    def test_no_html_comments_on_any_page(self, client: Client):
        """Notes for whoever edits the content belong in the template, not in the page.

        A {% comment %} block is stripped when Django renders, but an HTML
        comment in a content .md file is passed straight through by Markdown
        and served to the browser, where it shows up in view-source.
        """
        for path in ContentSitemap().items():
            html = client.get(path).content.decode()
            assert "<!--" not in html, f"HTML comment served on {path}"
