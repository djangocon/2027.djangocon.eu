from django.conf import settings

from djangocon.site.utils.content import get_navigation


def links(request):
    """Expose the nav and social links from content/navigation.json to every template."""
    return get_navigation()


def analytics(request):
    """Expose the GA4 measurement ID so base.html can decide whether to load the tag."""
    return {"ga4_measurement_id": settings.GA4_MEASUREMENT_ID}
