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

