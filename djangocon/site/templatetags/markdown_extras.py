import os

import markdown as md
from django import template
from django.core.cache import cache
from django.template.defaultfilters import stringfilter

register = template.Library()


def render_markdown_file(path):
    """Parse a content .md file into {"html", "meta"}, cached until the file changes."""
    mtime = os.path.getmtime(path)
    cache_key = f"markdown_extras:{path}:{mtime}"
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    with open(path) as f:
        source = f.read()
    m = md.Markdown(
        extensions=[
            "extra",
            "nl2br",
            "sane_lists",
            "meta",
            "toc",
        ]
    )
    result = {"html": m.convert(source), "meta": m.Meta}
    cache.set(cache_key, result, timeout=None)
    return result


@register.filter()
@stringfilter
def markdown(value):
    return render_markdown_file(value)


@register.filter
def get_bg_type(counter):
    return counter % 2 == 0 and "dark-background" or "light-background"
