import os


AUTH_USER_MODEL = "accounts.User"

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]

# Login/logout URLs
LOGIN_URL = "/auth/login/"
LOGIN_REDIRECT_URL = "/status/"
LOGOUT_REDIRECT_URL = LOGIN_URL

# Microsoft authentication
MICROSOFT_AUTH_TENANT_ID = os.environ.get("MICROSOFT_AUTH_TENANT_ID")
MICROSOFT_AUTH_CLIENT_ID = os.environ.get("MICROSOFT_AUTH_CLIENT_ID")
MICROSOFT_AUTH_CLIENT_SECRET = os.environ.get("MICROSOFT_AUTH_CLIENT_SECRET")
MICROSOFT_AUTH_LOGIN_TYPE = "ma"

# Authentication backends
AUTHENTICATION_BACKENDS = [
    "microsoft_auth.backends.MicrosoftAuthenticationBackend",
    "django.contrib.auth.backends.ModelBackend",
]
