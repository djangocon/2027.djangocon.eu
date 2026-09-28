"""robots.txt, sitemap.xml, the consent-gated analytics tag, and the served markup."""

import json
import re
from http import HTTPStatus

import pytest
from django.contrib.staticfiles import finders
from django.test import Client
from PIL import Image

from djangocon.site import sitemaps
from djangocon.site.sitemaps import ContentSitemap
from djangocon.site.utils.content import DESCRIPTION_LENGTH
from djangocon.site.utils.content import MIN_DESCRIPTION_LENGTH
from djangocon.site.utils.content import content_dir


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


class TestTicketLinkTracking:
    """Clicks through to the Pretix shop, measured as select_ticket_link."""

    def test_tracker_is_set_up_when_configured(self, client: Client, settings):
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        html = client.get("/").content.decode()
        assert "select_ticket_link" in html

    def test_absent_when_no_measurement_id_is_configured(self, client: Client, settings):
        """No tag means nothing to report to, so the listener must not ship either."""
        settings.GA4_MEASUREMENT_ID = ""
        assert "select_ticket_link" not in client.get("/").content.decode()

    def test_matches_the_configured_shop_host(self, client: Client, settings):
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        settings.PRETIX_HOST = "pretix.example.org"
        html = client.get("/").content.decode()
        assert "var PRETIX_HOST = 'pretix.example.org'" in html

    def test_sends_the_hit_by_beacon(self, client: Client, settings):
        """A plain request would be cancelled when the click navigates away."""
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        assert "'beacon'" in client.get("/").content.decode()

    def test_does_not_use_the_ecommerce_funnel_events(self, client: Client, settings):
        """The purchase happens on Pretix, so we cannot honestly report a checkout."""
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        html = client.get("/").content.decode()
        assert "begin_checkout" not in html
        assert "purchase" not in html

    def test_the_home_page_actually_links_to_that_host(self, client: Client, settings):
        """The tracker matches on the host, so a drifted link would go unmeasured."""
        settings.GA4_MEASUREMENT_ID = "G-TESTID1234"
        html = client.get("/").content.decode()
        assert f"https://{settings.PRETIX_HOST}/" in html


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


class TestSocialCard:
    def test_image_declares_its_size(self, client: Client):
        html = client.get("/").content.decode()
        width = int(re.search(r'og:image:width" content="(\d+)"', html).group(1))
        height = int(re.search(r'og:image:height" content="(\d+)"', html).group(1))
        with Image.open(finders.find("images/other/opengraph.jpg")) as image:
            assert image.size == (width, height)


class TestStructuredData:
    """schema.org JSON-LD: what makes the conference eligible for event results."""

    def _graph(self, client: Client, path: str = "/") -> list[dict]:
        html = client.get(path).content.decode()
        blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
        return [node for block in blocks for node in json.loads(block)["@graph"]]

    def test_home_page_describes_the_event(self, client: Client):
        event = next(node for node in self._graph(client) if node["@type"] == "Event")
        assert event["startDate"] == "2027-02-17"
        assert event["endDate"] == "2027-02-21"
        assert event["location"][0]["address"]["addressLocality"] == "Innsbruck"
        assert event["offers"]["url"].startswith("https://pretix.")

    def test_is_valid_json_with_the_social_profiles(self, client: Client):
        organization = next(node for node in self._graph(client) if node["@type"] == "Organization")
        assert "https://github.com/djangocon/2027.djangocon.eu/" in organization["sameAs"]

    def test_lowest_price_matches_the_ticket_cards(self, client: Client):
        """Google drops event markup that disagrees with the visible page."""
        html = client.get("/").content.decode()
        prices = [int(p) for p in re.findall(r'<div class="price">(\d+)€</div>', html)]
        event = next(node for node in self._graph(client) if node["@type"] == "Event")
        assert int(event["offers"]["lowPrice"]) == min(prices)

    def test_only_on_the_home_page(self, client: Client):
        assert self._graph(client, "/information/venue/") == []


class TestMetaDescription:
    def _description(self, client: Client, path: str) -> str:
        html = client.get(path).content.decode()
        return re.search(r'<meta name="description"\s+content="([^"]*)"', html).group(1)

    def test_every_page_has_its_own(self, client: Client):
        """Identical descriptions make search engines treat pages as near-duplicates."""
        paths = ContentSitemap().items()
        descriptions = [self._description(client, path) for path in paths]
        duplicates = {d for d in descriptions if descriptions.count(d) > 1}
        assert not duplicates, f"shared meta description: {duplicates}"

    def test_fits_a_search_snippet(self, client: Client):
        for path in ContentSitemap().items():
            assert MIN_DESCRIPTION_LENGTH <= len(self._description(client, path)) <= DESCRIPTION_LENGTH, path

    def test_explicit_metadata_wins(self, client: Client):
        assert self._description(client, "/talks/cfp/").startswith("Submit a talk or workshop")

    def test_social_card_uses_the_same_text(self, client: Client):
        html = client.get("/information/venue/").content.decode()
        og = re.search(r'og:description"\s+content="([^"]*)"', html).group(1)
        assert og == self._description(client, "/information/venue/")

    def test_error_pages_fall_back_to_the_site_description(self, client: Client):
        html = client.get("/no-such-page/").content.decode()
        assert "The official Django conference in Europe" in html


class TestTitle:
    def _title(self, client: Client, path: str) -> str:
        html = client.get(path).content.decode()
        return " ".join(re.search(r"<title>(.*?)</title>", html, re.S).group(1).split())

    def test_home_names_the_place_and_dates(self, client: Client):
        title = self._title(client, "/")
        assert "Innsbruck" in title
        assert "February" in title

    def test_pages_lead_with_their_own_name(self, client: Client):
        assert self._title(client, "/information/venue/") == "Venue - DjangoCon Europe 2027"


class TestSitemapLastmod:
    """lastmod must follow content changes, not deploys."""

    def test_uses_the_last_commit_when_git_is_available(self):
        path = content_dir() / "talks" / "cfp" / "0_cfp.md"
        sitemaps._committed_at.cache_clear()
        committed = sitemaps._committed_at((path,))
        if committed is None:
            pytest.skip("no git history available here")
        assert sitemaps.last_changed([path]) == committed

    def test_falls_back_to_the_file_time_without_git(self, monkeypatch):
        path = content_dir() / "talks" / "cfp" / "0_cfp.md"
        monkeypatch.setattr(sitemaps, "_GIT", None)
        sitemaps._committed_at.cache_clear()
        try:
            assert sitemaps.last_changed([path]) == path.stat().st_mtime
        finally:
            sitemaps._committed_at.cache_clear()
