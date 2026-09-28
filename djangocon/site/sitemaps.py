"""Sitemap for the content pages.

The site has no models, so there is nothing for Django to enumerate on its
own. The URL list is instead walked out of ``content/``, the same tree the
pages themselves are rendered from, so adding a page adds a sitemap entry
with no extra step and the sitemap cannot drift out of date.
"""

import shutil
import subprocess
from functools import cache
from pathlib import Path

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.utils import timezone

from djangocon.site.utils.content import content_dir
from djangocon.site.utils.content import page_files

_GIT = shutil.which("git")


@cache
def _committed_at(paths: tuple[Path, ...]) -> float | None:
    """Unix time of the last commit touching ``paths``, or None without git.

    Cached for the process: a deploy restarts it, and that is the only time
    committed history changes under a running site.
    """
    if _GIT is None:
        return None
    try:
        result = subprocess.run(  # noqa: S603 -- fixed argv, paths come from our own content tree
            [_GIT, "log", "-1", "--format=%ct", "--", *map(str, paths)],
            cwd=settings.BASE_DIR,
            capture_output=True,
            text=True,
            timeout=5,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return float(result.stdout) if result.stdout.strip() else None


def last_changed(paths: list[Path]) -> float:
    """When the content behind a page last changed, as a Unix time.

    The last commit is the honest answer: a fresh checkout or a container
    build stamps every file with the deploy time, and a lastmod that jumps
    for every URL on every deploy teaches search engines to ignore it. The
    file mtime stands in where there is no git, or for files git has never
    seen.
    """
    return _committed_at(tuple(sorted(paths))) or max(path.stat().st_mtime for path in paths)


# "/<menu>/" -- a leading and a trailing slash. Deeper URLs have more.
_TOP_LEVEL_SLASHES = 2


class ContentSitemap(Sitemap):
    """Every URL the site actually serves, discovered from the content tree."""

    protocol = "https"
    changefreq = "weekly"

    def items(self) -> list[str]:
        """Home plus every ``content/<menu>[/<submenu>]`` folder that renders a page.

        A folder with no published ``.md`` raises 404 in the view, so it is
        skipped here too rather than advertising a dead URL to crawlers.
        ``content/home`` is excluded because it is served at ``/`` -- ``/home/``
        is only kept as a permanent redirect, and a sitemap should list the
        canonical URL.
        """
        paths = ["/"]
        for menu in sorted(p for p in content_dir().iterdir() if p.is_dir()):
            if menu.name == "home":
                continue
            if page_files(menu):
                paths.append(f"/{menu.name}/")
            paths.extend(
                f"/{menu.name}/{submenu.name}/"
                for submenu in sorted(p for p in menu.iterdir() if p.is_dir())
                if page_files(submenu)
            )
        return paths

    def location(self, item: str) -> str:
        return item

    def priority(self, item: str) -> float:
        """The home page first, then top-level pages, then the deeper ones."""
        if item == "/":
            return 1.0
        # "/talks/" has two slashes, "/talks/cfp/" three.
        return 0.8 if item.count("/") == _TOP_LEVEL_SLASHES else 0.6

    def lastmod(self, item: str):
        """When the files that make up the page last changed (see ``last_changed``)."""
        directory = content_dir() / "home" if item == "/" else content_dir().joinpath(*item.strip("/").split("/"))
        files = page_files(directory)
        if not files:
            return None
        newest = last_changed(list(files.values()))
        return timezone.datetime.fromtimestamp(newest, tz=timezone.get_current_timezone())


SITEMAPS = {"content": ContentSitemap()}
