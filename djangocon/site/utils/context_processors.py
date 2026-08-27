from djangocon.site.utils.content import get_navigation


def links(request):
    """Expose the nav and social links from content/navigation.json to every template."""
    return get_navigation()
