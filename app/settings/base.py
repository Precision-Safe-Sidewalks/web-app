# ruff: noqa
import os
from pathlib import Path

from app.settings.auth import *
from app.settings.aws import *
from app.settings.cors import *
from app.settings.db import *
from app.settings.drf import *
from app.settings.logs import *
from app.settings.storage import *

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# General settings
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY")
DEBUG = True
ALLOWED_HOSTS = ["*"]
ROOT_URLCONF = "app.urls"
WSGI_APPLICATION = "app.wsgi.application"
APPEND_SLASH = True
SITE_ID = 1


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.gis",
    "django_extensions",
    "compressor",
    "corsheaders",
    "microsoft_auth",
    "rest_framework",
    "rest_framework_gis",
    "django_filters",
    "accounts",
    "core",
    "customers",
    "pages",
    "repairs",
]


# Middleware definition
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "app.middleware.AuthMiddleware",
]


# Template definition
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [
            BASE_DIR / "templates",
            BASE_DIR / "templates/fragments",
        ],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"
STATIC_ROOT = "static/"
STATICFILES_DIRS = []

STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
    "compressor.finders.CompressorFinder",
]

COMPRESS_PRECOMPILERS = [
    ("text/x-scss", "django_libsass.SassCompiler"),
]


# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# FIXME: disable once using HTTPS
SECURE_CROSS_ORIGIN_OPENER_POLICY = None

# Measurement geocoding queue URL
MEASUREMENT_GEOCODING_QUEUE_URL = os.environ.get("MEASUREMENT_GEOCODING_QUEUE_URL")
