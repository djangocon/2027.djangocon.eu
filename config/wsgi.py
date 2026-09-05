"""
WSGI config for the DjangoCon Europe site.

Exposes the WSGI callable as a module-level variable named ``application``.
The settings module is taken from the environment (DJANGO_SETTINGS_MODULE)
and defaults to production.
"""

import os
import sys
from pathlib import Path

from django.core.wsgi import get_wsgi_application

# This allows easy placement of apps within the interior djangocon directory.
BASE_DIR = Path(__file__).resolve(strict=True).parent.parent
sys.path.append(str(BASE_DIR / "djangocon"))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.production")

application = get_wsgi_application()
