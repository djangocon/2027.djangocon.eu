from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_safe

from djangocon.site.utils.content import content_dir
from djangocon.site.utils.content import get_sponsors
from djangocon.site.utils.content import page_files
from djangocon.site.utils.content import render_markdown_file


def _title(slug: str) -> str:
    return slug.replace("_", " ").title()


@require_safe
def home(request):
    files = page_files(content_dir() / "home")
    return render(request, "pages/home.html", {"menu": "Home", "files": files, "sponsors": get_sponsors()})


@require_safe
def sponsors(request):
    sponsors_page = content_dir() / "sponsors" / "sponsors" / "sponsors.md"
    ctx = {"menu": "Sponsors", "content": render_markdown_file(sponsors_page), "sponsors": get_sponsors()}
    return render(request, "modules/sponsor_page.html", ctx)


@require_safe
def page(request, menu, submenu=None):
    """A content page: every ``.md`` under ``content/<menu>/[<submenu>/]`` becomes a section."""
    directory = content_dir() / menu / submenu if submenu else content_dir() / menu
    files = page_files(directory)
    if not files:
        raise Http404
    return render(request, "pages/default.html", {"menu": _title(submenu or menu), "files": files})
