"""schema.org JSON-LD for search engines.

Built here rather than written out in a template: djLint's formatter treats a
<script> body as JavaScript and mangles any template tag inside it, and
json.dumps gets the escaping right for free.

Every value is repeated from somewhere a visitor can read it, and Google
drops markup that disagrees with the page, so keep them in step:

    dates      content/home/dates.md (main conference + sprints)
    location   content/information/venue/0_venue.md
    low price  the cheapest "from" price in templates/modules/home_tickets.html
    tickets    the Pretix link used across the site

Online tickets are sold too, hence MixedEventAttendanceMode and a
VirtualLocation next to the venue.
"""

import json

from django import template
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from djangocon.site.utils.content import get_navigation

register = template.Library()

SITE = "https://2027.djangocon.eu"
TICKETS_URL = "https://pretix.evolutio.pt/evolutio/djceu27/"


def home_graph() -> list[dict]:
    """The Event, and the Organization and WebSite it belongs to."""
    organization = f"{SITE}/#organization"
    return [
        {
            "@type": "Event",
            "@id": f"{SITE}/#event",
            "name": "DjangoCon Europe 2027",
            "description": (
                "The official Django conference in Europe - run by the community for the community. "
                "Three days of talks and two days of sprints in Innsbruck, Austria."
            ),
            "url": f"{SITE}/",
            "image": SITE + static("images/other/opengraph.jpg"),
            "startDate": "2027-02-17",
            "endDate": "2027-02-21",
            "eventStatus": "https://schema.org/EventScheduled",
            "eventAttendanceMode": "https://schema.org/MixedEventAttendanceMode",
            "inLanguage": "en",
            "location": [
                {
                    "@type": "Place",
                    "name": "SoWi University Innsbruck",
                    "address": {
                        "@type": "PostalAddress",
                        "streetAddress": "Universitätsstrasse 15",
                        "postalCode": "6020",
                        "addressLocality": "Innsbruck",
                        "addressRegion": "Tyrol",
                        "addressCountry": "AT",
                    },
                    "geo": {"@type": "GeoCoordinates", "latitude": 47.26986, "longitude": 11.398466},
                },
                {"@type": "VirtualLocation", "url": f"{SITE}/"},
            ],
            "offers": {
                "@type": "AggregateOffer",
                "url": TICKETS_URL,
                "lowPrice": "59",
                "priceCurrency": "EUR",
                "availability": "https://schema.org/InStock",
            },
            "organizer": {"@id": organization},
        },
        {
            "@type": "Organization",
            "@id": organization,
            "name": "DjangoCon Europe",
            "url": f"{SITE}/",
            "logo": SITE + static("images/favicons/android-chrome-512x512.png"),
            "sameAs": list(get_navigation().get("social_media", {}).values()),
        },
        {
            "@type": "WebSite",
            "@id": f"{SITE}/#website",
            "name": "DjangoCon Europe 2027",
            "url": f"{SITE}/",
            "publisher": {"@id": organization},
        },
    ]


@register.simple_tag
def home_json_ld():
    """``<script type="application/ld+json">`` for the home page."""
    data = json.dumps({"@context": "https://schema.org", "@graph": home_graph()}, ensure_ascii=False)
    # "</" would close the <script> early; "<\/" means the same thing in JSON.
    return format_html('<script type="application/ld+json">{}</script>', mark_safe(data.replace("</", "<\\/")))  # noqa: S308
