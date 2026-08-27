from os import listdir

from django.http import Http404
from django.shortcuts import render

from config.settings.base import APPS_DIR
from djangocon.site.templatetags.markdown_extras import render_markdown_file
from djangocon.site.utils.content import get_sponsors

CONTENT_DIR = APPS_DIR / "content"
SPONSORS_PAGE = CONTENT_DIR / "sponsors" / "sponsors" / "sponsors.md"


def _page_files(directory):
    """Content files in `directory`, ordered by their `order:` metadata then name."""
    if not directory.is_dir():
        return {}

    def sort_key(name):
        order = render_markdown_file(directory / name)["meta"].get("order", [None])[0]
        try:
            return (0, float(order))
        except (TypeError, ValueError):
            return (1, name)

    names = sorted(
        (f for f in listdir(directory) if f.endswith(".md")),
        key=sort_key,
    )
    return {name.removesuffix(".md"): directory / name for name in names}


def default_view(request, menu="home", submenu=None):
    directory = CONTENT_DIR / menu / submenu if submenu else CONTENT_DIR / menu
    files = _page_files(directory)

    ctx = {
        "menu": (submenu or menu).replace("_", " ").title(),
        "files": files,
    }

    if menu == "home":
        template = "pages/home.html"
        ctx["files"]["home"] = SPONSORS_PAGE
        ctx["sponsors"] = get_sponsors()
    elif menu == "sponsors" and submenu == "sponsors":
        template = "modules/sponsor_page.html"
        ctx["sponsors"] = get_sponsors()
        ctx["content"] = render_markdown_file(SPONSORS_PAGE)
    elif not files:
        raise Http404(f"No content for /{menu}/")
    else:
        template = "pages/default.html"

    return render(request, template, ctx)
