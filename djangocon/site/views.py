from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.views.decorators.http import require_safe

from djangocon.site.utils.content import content_dir
from djangocon.site.utils.content import get_navigation
from djangocon.site.utils.content import get_sponsors
from djangocon.site.utils.content import page_files


def _title(path: str, slug: str) -> str:
    """The page's name, taken from its menu label.

    Title-casing the URL slug produced "Cfp", "Tshirts" and "Code Of Conduct",
    and could not know that /information/social_events/ is called "Party". The
    navigation is where a page's name is actually decided, so read it there and
    fall back to the slug only for pages that are not in the menu.
    """
    for item in get_navigation().get("site_menu", {}).values():
        for label, href in item.get("submenu", {}).items():
            if href == path:
                return label
    return slug.replace("_", " ").title()


@require_safe
def home(request):
    files = page_files(content_dir() / "home")
    return render(request, "pages/home.html", {"menu": "Home", "files": files, "sponsors": get_sponsors()})


@require_safe
def sponsors(request):
    """Same page pipeline as every other content page, plus the sponsor list."""
    files = page_files(content_dir() / "sponsors" / "sponsors")
    return render(request, "pages/default.html", {"menu": "Sponsors", "files": files, "sponsors": get_sponsors()})


@require_safe
def page(request, menu, submenu=None):
    """A content page: every ``.md`` under ``content/<menu>/[<submenu>/]`` becomes a section."""
    directory = content_dir() / menu / submenu if submenu else content_dir() / menu
    files = page_files(directory)
    if not files:
        raise Http404
    return render(request, "pages/default.html", {"menu": _title(request.path, submenu or menu), "files": files})


@require_safe
def robots_txt(request):
    """/robots.txt, pointing crawlers at the sitemap.

    The sitemap URL has to be absolute -- a relative one is ignored -- and is
    built from the request so it stays right on any host the site is served
    from, rather than hardcoding the production domain into a file that also
    gets served in development.
    """
    sitemap_url = request.build_absolute_uri(reverse("django.contrib.sitemaps.views.sitemap"))
    return render(request, "robots.txt", {"sitemap_url": sitemap_url}, content_type="text/plain")
