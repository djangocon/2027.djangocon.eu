"""Loaders for the site content: Markdown pages and the JSON data files.

Everything is read from ``settings.CONTENT_DIR``. Both the Markdown files and
the JSON data files are re-read when their mtime changes, so an edit shows up
without a restart -- ``runserver`` only reloads on ``.py`` changes, so caching
the JSON for the process lifetime left a stale menu pointing at deleted pages.
"""

import json
import re
from pathlib import Path

import markdown as md
from django.conf import settings
from django.templatetags.static import static

_MARKDOWN_EXTENSIONS = ["extra", "nl2br", "sane_lists", "meta", "toc"]

# A "/static/..." URL written by hand in a content file: in an attribute
# (src="/static/..."), a srcset list, or a Markdown link.
_STATIC_URL = re.compile(r"""(?<=["'\s,(])/static/([^\s"'(),?#]+)""")

# path -> (mtime, parsed). Both are bounded by the number of content files.
_markdown_cache: dict[Path, tuple[float, dict]] = {}
_json_cache: dict[Path, tuple[float, dict]] = {}


def content_dir() -> Path:
    return Path(settings.CONTENT_DIR)


def _static_url(match: re.Match) -> str:
    """The storage's URL for a static file -- the hashed name in production.

    Only hashed names get WhiteNoise's year-long immutable cache header; a
    plain "/static/x.png" is revalidated every minute. A path missing from the
    manifest is left as written rather than turning the page into a 500.
    """
    try:
        return static(match.group(1))
    except ValueError:
        return match.group(0)


def resolve_static_urls(html: str) -> str:
    """Swap hand-written ``/static/...`` URLs for what ``{% static %}`` would output."""
    return _STATIC_URL.sub(_static_url, html)


def render_markdown_file(path: Path) -> dict:
    """Parse a content .md file into ``{"html", "meta"}``, re-parsing only when it changes."""
    mtime = path.stat().st_mtime
    cached = _markdown_cache.get(path)
    if cached is not None and cached[0] == mtime:
        return cached[1]

    parser = md.Markdown(extensions=_MARKDOWN_EXTENSIONS)
    html = resolve_static_urls(parser.convert(path.read_text(encoding="utf-8")))
    result = {"html": html, "meta": parser.Meta}
    _markdown_cache[path] = (mtime, result)
    return result


def is_published(path: Path) -> bool:
    """False only when a file opts out with ``published: false`` in its metadata.

    Lets a section be parked without deleting it.
    """
    value = render_markdown_file(path)["meta"].get("published", [None])[0]
    return str(value).strip().lower() not in {"false", "no", "0"}


def page_files(directory: Path) -> dict[str, Path]:
    """Published content files in ``directory`` keyed by stem, ordered by ``order:`` then name."""
    if not directory.is_dir():
        return {}

    def sort_key(path: Path):
        order = render_markdown_file(path)["meta"].get("order", [None])[0]
        try:
            return (0, float(order), path.name)
        except (TypeError, ValueError):
            return (1, 0.0, path.name)

    files = (path for path in directory.glob("*.md") if is_published(path))
    return {path.stem: path for path in sorted(files, key=sort_key)}


def _load_json(name: str) -> dict:
    """Parse a content .json file, re-reading only when it changes."""
    path = content_dir() / name
    mtime = path.stat().st_mtime
    cached = _json_cache.get(path)
    if cached is not None and cached[0] == mtime:
        return cached[1]

    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    # Keys starting with "_" are editor notes, not content.
    result = {k: v for k, v in data.items() if not k.startswith("_")}
    _json_cache[path] = (mtime, result)
    return result


def get_sponsors() -> dict:
    """Sponsors by tier, with empty tiers dropped so the template can loop blindly."""
    return {tier: entries for tier, entries in _load_json("sponsors.json").items() if entries}


def get_navigation() -> dict:
    """Menu structure and social links."""
    return _load_json("navigation.json")
