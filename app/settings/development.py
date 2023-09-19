# ruff: noqa
import sys

from app.settings.base import *

# For testing, override the static files storage
if "test" in sys.argv:
    STORAGES["staticfiles"] = {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    }
