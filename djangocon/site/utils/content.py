"""Loaders for the JSON data files that sit alongside the markdown content.

Both files are read once per process. They only change on deploy, so there is
no cache to invalidate and no per-request file access.
"""

import json
from functools import lru_cache

from config.settings.base import APPS_DIR

CONTENT_DIR = APPS_DIR / "content"


def _load(name):
    with open(CONTENT_DIR / name) as f:
        data = json.load(f)
    # Keys starting with "_" are editor notes, not content.
    return {k: v for k, v in data.items() if not k.startswith("_")}


@lru_cache(maxsize=1)
def get_sponsors():
    """Sponsors by tier, with empty tiers dropped so the template can loop blindly."""
    return {tier: entries for tier, entries in _load("sponsors.json").items() if entries}


@lru_cache(maxsize=1)
def get_navigation():
    """Menu structure and social links."""
    return _load("navigation.json")
