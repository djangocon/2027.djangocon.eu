from django.conf import settings

from djangocon.site.utils.content import get_navigation

SITE_DESCRIPTION = (
    "The official Django conference in Europe - run by the community for the community. "
    "Innsbruck, Austria, 17-21 February 2027."
)


def links(request):
    """Expose the nav and social links from content/navigation.json to every template.

    The site-wide description rides along: it is the fallback for pages that do
    not pass their own, and error pages render without a view's context.
    """
    return {**get_navigation(), "site_description": SITE_DESCRIPTION}


def analytics(request):
    """Expose the GA4 settings so base.html can decide whether to load the tag.

    The Pretix host travels with the measurement ID because the only thing that
    reads it is the ticket-link click tracker inside the same tag module.
    """
    return {
        "ga4_measurement_id": settings.GA4_MEASUREMENT_ID,
        "pretix_host": settings.PRETIX_HOST,
    }
