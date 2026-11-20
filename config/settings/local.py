import os

from django.core.management.utils import get_random_secret_key

from .base import *

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = True
# https://docs.djangoproject.com/en/dev/ref/settings/#secret-key
# Not env(..., default=...): django-environ re-expands "$" in a default value,
# and a generated key containing one sends it into infinite recursion.
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY") or get_random_secret_key()
# https://docs.djangoproject.com/en/dev/ref/settings/#allowed-hosts
ALLOWED_HOSTS = ["*"]

# CACHES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#caches
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "",
    }
}

# WhiteNoise
# ------------------------------------------------------------------------------
# http://whitenoise.evans.io/en/latest/django.html#using-whitenoise-in-development
INSTALLED_APPS = ["whitenoise.runserver_nostatic", *INSTALLED_APPS]

# Allow same-origin framing in dev so the site can be previewed inside a
# mobile-sized iframe (e.g. responsive checks); production stays DENY.
X_FRAME_OPTIONS = "SAMEORIGIN"
