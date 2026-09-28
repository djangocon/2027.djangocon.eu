"""What the served pages cost to load: asset bundles, images, caching."""

import re

from django.test import Client


class TestAssetBundles:
    def test_pages_load_the_minified_bundles(self, client: Client):
        """gulp builds both flavours; only the .min ones should reach visitors."""
        html = client.get("/").content.decode()
        for href in re.findall(r'(?:href|src)="([^"]+\.(?:css|js))"', html):
            if href.startswith("/static/"):
                assert ".min." in href, f"unminified asset served: {href}"
