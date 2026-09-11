"""
Base settings to build other settings files upon.
"""

from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent.parent
# djangocon/
APPS_DIR = BASE_DIR / "djangocon"
env = environ.Env()

READ_DOT_ENV_FILE = env.bool("DJANGO_READ_DOT_ENV_FILE", default=True)
if READ_DOT_ENV_FILE:
    # OS environment variables take precedence over variables from .env
    env.read_env(str(BASE_DIR / ".env"))

# GENERAL
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#debug
DEBUG = env.bool("DJANGO_DEBUG", False)
# Local time zone. Choices are
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# though not all of them may be available with every OS.
# In Windows, this must be set to your system time zone.
TIME_ZONE = "Europe/Vienna"
# https://docs.djangoproject.com/en/dev/ref/settings/#language-code
LANGUAGE_CODE = "en"
# The site is English-only and ships no translations.
# https://docs.djangoproject.com/en/dev/ref/settings/#use-i18n
USE_I18N = False
# https://docs.djangoproject.com/en/dev/ref/settings/#use-tz
USE_TZ = True

# CONTENT
# ------------------------------------------------------------------------------
# The site has no database: every page is rendered from the Markdown and JSON
# files in this directory. See djangocon/site/utils/content.py.
CONTENT_DIR = APPS_DIR / "content"

# ANALYTICS
# ------------------------------------------------------------------------------
# Google Analytics 4 measurement ID. Empty by default so local development and
# CI send no hits and do not pollute the property; production sets it (see
# config/settings/production.py). The tag is only loaded after the visitor
# accepts analytics cookies -- see templates/modules/analytics.html.
GA4_MEASUREMENT_ID = env("DJANGO_GA4_MEASUREMENT_ID", default="")
# Host of the Pretix ticket shop. The ticket links themselves are written out
# in full in the templates and in content/navigation.json; this is only the
# host the click tracker matches on, so that a link added later is measured
# without having to be tagged. Overridable by env so a staging shop still
# reports. See templates/modules/analytics_head.html.
PRETIX_HOST = env("DJANGO_PRETIX_HOST", default="pretix.evolutio.pt")

# URLS
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#root-urlconf
ROOT_URLCONF = "config.urls"
# https://docs.djangoproject.com/en/dev/ref/settings/#wsgi-application
WSGI_APPLICATION = "config.wsgi.application"

# APPS
# ------------------------------------------------------------------------------
# No models, no auth, no forms: only static files are needed from Django itself.
# sitemaps is the exception -- it needs no database here because the sitemap is
# built from the content files rather than from a queryset.
DJANGO_APPS = [
    "django.contrib.staticfiles",
    "django.contrib.sitemaps",
]
THIRD_PARTY_APPS = []
LOCAL_APPS = [
    "djangocon.site",
]
# https://docs.djangoproject.com/en/dev/ref/settings/#installed-apps
INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

# MIDDLEWARE
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# STATIC
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#static-root
STATIC_ROOT = str(BASE_DIR / "staticfiles")
# https://docs.djangoproject.com/en/dev/ref/settings/#static-url
STATIC_URL = "/static/"
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#std:setting-STATICFILES_DIRS
STATICFILES_DIRS = [str(APPS_DIR / "static")]
# https://docs.djangoproject.com/en/dev/ref/contrib/staticfiles/#staticfiles-finders
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

# TEMPLATES
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#templates
TEMPLATES = [
    {
        # https://docs.djangoproject.com/en/dev/ref/settings/#std:setting-TEMPLATES-BACKEND
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        # https://docs.djangoproject.com/en/dev/ref/settings/#dirs
        "DIRS": [str(APPS_DIR / "templates")],
        # https://docs.djangoproject.com/en/dev/ref/settings/#app-dirs
        "APP_DIRS": True,
        "OPTIONS": {
            # https://docs.djangoproject.com/en/dev/ref/settings/#template-context-processors
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "djangocon.site.utils.context_processors.links",
                "djangocon.site.utils.context_processors.analytics",
            ],
        },
    }
]

# SECURITY
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#x-frame-options
X_FRAME_OPTIONS = "DENY"
# The site has no forms or sessions, so CsrfViewMiddleware is deliberately absent.
SILENCED_SYSTEM_CHECKS = ["security.W003"]

# LOGGING
# ------------------------------------------------------------------------------
# https://docs.djangoproject.com/en/dev/ref/settings/#logging
# See https://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"verbose": {"format": "%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d %(message)s"}},
    "handlers": {
        "console": {
            "level": "DEBUG",
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        }
    },
    "root": {"level": "INFO", "handlers": ["console"]},
}
