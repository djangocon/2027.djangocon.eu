"""The Discord invite: header links and the /discord/ short link."""

from http import HTTPStatus

from django.test import Client

from djangocon.site.utils.content import get_navigation

INVITE = get_navigation()["social_media"]["discord"]


class TestDiscordShortLink:
    def test_redirects_to_the_invite(self, client: Client):
        response = client.get("/discord/")
        assert response.status_code == HTTPStatus.FOUND
        assert response["Location"] == INVITE

    def test_redirect_is_temporary(self, client: Client):
        """Invites get replaced; a 301 would stay cached pointing at the old one."""
        assert client.get("/discord/").status_code != HTTPStatus.MOVED_PERMANENTLY

    def test_rejects_writes(self, client: Client):
        assert client.post("/discord/").status_code == HTTPStatus.METHOD_NOT_ALLOWED


class TestDiscordInHeader:
    def test_icon_in_the_always_visible_actions(self, client: Client):
        """One button for every width: it sits with the actions, not in the collapsible menu."""
        body = client.get("/").content.decode()
        actions = body.split('class="header-actions"', 1)[1].split('id="mobileNav"', 1)[0]
        assert f'href="{INVITE}"' in actions
        assert body.count('class="discord-btn"') == 1

    def test_is_icon_only_with_an_accessible_name(self, client: Client):
        body = client.get("/").content.decode()
        button = body.split('class="discord-btn"', 1)[1].split("</a>", 1)[0]
        assert 'aria-label="Join us on Discord"' in button
        assert "<span" not in button

    def test_on_every_page(self, client: Client):
        assert "discord-btn" in client.get("/talks/cfp/").content.decode()


class TestHeaderActions:
    def test_tickets_and_theme_stay_out_of_the_collapsible_menu(self, client: Client):
        body = client.get("/").content.decode()
        actions = body.split('class="header-actions"', 1)[1].split('id="mobileNav"', 1)[0]
        assert 'id="navbar-hero-btn"' in actions
        assert 'id="theme-toggle"' in actions
        assert "navbar-toggler" in actions
