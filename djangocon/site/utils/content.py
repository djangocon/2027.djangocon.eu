"""Loaders for the site content: Markdown pages and the JSON data files.

Everything is read from ``settings.CONTENT_DIR``. The JSON files are read once
per process (they only change on deploy). Markdown files are re-parsed when
their mtime changes, so the dev server picks up edits without a restart.
"""

import json
from functools import lru_cache
from pathlib import Path

import markdown as md
from django.conf import settings

_MARKDOWN_EXTENSIONS = ["extra", "nl2br", "sane_lists", "meta", "toc"]

# path -> (mtime, {"html", "meta"}). Bounded by the number of content files.
_markdown_cache: dict[Path, tuple[float, dict]] = {}


def content_dir() -> Path:
    return Path(settings.CONTENT_DIR)


def render_markdown_file(path: Path) -> dict:
    """Parse a content .md file into ``{"html", "meta"}``, re-parsing only when it changes."""
    mtime = path.stat().st_mtime
    cached = _markdown_cache.get(path)
    if cached is not None and cached[0] == mtime:
        return cached[1]

    parser = md.Markdown(extensions=_MARKDOWN_EXTENSIONS)
    result = {"html": parser.convert(path.read_text(encoding="utf-8")), "meta": parser.Meta}
    _markdown_cache[path] = (mtime, result)
    return result


def page_files(directory: Path) -> dict[str, Path]:
    """Content files in ``directory`` keyed by stem, ordered by ``order:`` metadata then name."""
    if not directory.is_dir():
        return {}

    def sort_key(path: Path):
        order = render_markdown_file(path)["meta"].get("order", [None])[0]
        try:
            return (0, float(order), path.name)
        except (TypeError, ValueError):
            return (1, 0.0, path.name)

    return {path.stem: path for path in sorted(directory.glob("*.md"), key=sort_key)}


def _load_json(name: str) -> dict:
    with (content_dir() / name).open(encoding="utf-8") as f:
        data = json.load(f)
    # Keys starting with "_" are editor notes, not content.
    return {k: v for k, v in data.items() if not k.startswith("_")}


@lru_cache(maxsize=1)
def get_sponsors() -> dict:
    """Sponsors by tier, with empty tiers dropped so the template can loop blindly."""
    return {tier: entries for tier, entries in _load_json("sponsors.json").items() if entries}


@lru_cache(maxsize=1)
def get_navigation() -> dict:
    """Menu structure and social links."""
    return _load_json("navigation.json")
