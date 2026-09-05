from django import template
from django.template.loader import select_template

from djangocon.site.utils.content import render_markdown_file

register = template.Library()

# Content files that name a layout with no matching template fall back to this,
# so a typo in a .md file degrades to a plain page instead of a 500.
FALLBACK_LAYOUT = "simple"


@register.filter
def markdown(path):
    """Render a content file path to ``{"html", "meta"}``."""
    return render_markdown_file(path)


@register.filter
def layout_template(content):
    """Template path for a parsed file's ``layout:``, falling back when it's missing."""
    layout = content["meta"].get("layout", [None])[0]
    candidates = [f"modules/{layout}.html"] if layout else []
    candidates.append(f"modules/{FALLBACK_LAYOUT}.html")
    return select_template(candidates).template.name


@register.filter
def meta(content, key):
    """First value of a metadata key, or an empty string (``content|meta:"title"``)."""
    return content["meta"].get(key, [""])[0]


@register.filter
def get_bg_type(counter):
    return "dark-background" if counter % 2 == 0 else "light-background"
