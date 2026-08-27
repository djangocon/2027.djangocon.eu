import markdown as md
from django import template
from django.template.loader import select_template

register = template.Library()

# Content files that name a layout with no matching template fall back to this,
# so a typo in a .md file degrades to a plain page instead of a 500.
FALLBACK_LAYOUT = "simple"

_EXTENSIONS = ["extra", "nl2br", "sane_lists", "meta", "toc"]

# path -> (mtime, {"html", "meta"}). Bounded by the number of content files, and
# re-parsed when a file changes so the dev server picks up edits without a restart.
_cache = {}


def render_markdown_file(path):
    """Parse a content .md file into {"html", "meta"}, re-parsing only when it changes."""
    mtime = path.stat().st_mtime
    cached = _cache.get(path)
    if cached is not None and cached[0] == mtime:
        return cached[1]

    parser = md.Markdown(extensions=_EXTENSIONS)
    result = {"html": parser.convert(path.read_text()), "meta": parser.Meta}
    _cache[path] = (mtime, result)
    return result


@register.filter
def markdown(value):
    return render_markdown_file(value)


@register.filter
def layout_template(content):
    """Template path for a parsed file's `layout:`, falling back when it's missing."""
    layout = content["meta"].get("layout", [None])[0]
    candidates = [f"modules/{layout}.html"] if layout else []
    candidates.append(f"modules/{FALLBACK_LAYOUT}.html")
    return select_template(candidates).template.name


@register.filter
def get_bg_type(counter):
    return "dark-background" if counter % 2 == 0 else "light-background"
