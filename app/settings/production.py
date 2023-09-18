# ruff: noqa
from app.settings.base import *

DEBUG = True

ALLOWED_HOSTS = [
    "*",
]

CSRF_TRUSTED_ORIGINS = [
    "https://*.bluezoneautomation.com",
]
