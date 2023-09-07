# ruff: noqa
from app.settings.base import *

DEBUG = False

ALLOWED_HOSTS = [
    "pss-production-1462576609.us-east-1.elb.amazonaws.com", # FIXME: replace with production domains
]
