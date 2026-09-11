from django.conf import settings

from djangocon.site.utils.content import get_navigation


def links(request):
    """Expose the nav and social links from content/navigation.json to every template."""
    return get_navigation()


def analytics(request):
    """Expose the GA4 settings so base.html can decide whether to load the tag.

    The Pretix host travels with the measurement ID because the only thing that
    reads it is the ticket-link click tracker inside the same tag module.
    """
    return {
        "ga4_measurement_id": settings.GA4_MEASUREMENT_ID,
        "pretix_host": settings.PRETIX_HOST,
    }
