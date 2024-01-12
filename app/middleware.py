import json
import logging
import re
from functools import cache

import jwt
import requests
from django.conf import settings
from django.contrib.auth import get_user_model
from django.http import HttpResponseRedirect
from django.urls import reverse


LOGGER = logging.getLogger(__name__)
User = get_user_model()


class AuthMiddleware:
    """Middleware to programatically check user authentication"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Pre-process the request to check if auth is required"""
        if self.is_public(request.path):
            return self.get_response(request)

        AzureADAuthenticator().authenticate(request)

        if request.user.is_authenticated:
            return self.get_response(request)

        if self.is_lambda(request):
            return self.get_response(request)

        login_url = reverse("login") + f"?next={request.path}"
        return HttpResponseRedirect(login_url)

    def is_public(self, url):
        """Return True if the URL is public"""
        return any(re.match(pattern, url) for pattern in settings.PUBLIC_URLS)

    def is_lambda(self, request):
        """Return True if the request is authenticated as a Lambda function"""
        header = str(request.headers.get("Authorization"))
        token = header.replace("Token ", "").strip()
        return settings.LAMBDA_API_KEY == token


class AzureADAuthenticator:
    """Azure AD token authenticator"""

    def authenticate(self, request):
        """Authenticate a user with an Azure AD token"""
        token = self._get_token(request)

        if token:
            public_keys = self._get_public_keys()

            header = jwt.get_unverified_header(token)
            kid = header["kid"]
            alg = header["alg"]
            key = public_keys.get(kid)
            aud = settings.MICROSOFT_AUTH_CLIENT_ID

            try:
                claims = jwt.decode(token, key=key, audience=aud, algorithms=[alg])
                user = User.objects.filter(
                    email=claims["email"], is_active=True
                ).first()

                if user is not None:
                    request.user = user
                    return True

            except jwt.exceptions.InvalidTokenError as exc:
                return False

        return False

    def _get_token(self, request):
        """Return the Bearer token from the Authorization header"""
        if header := request.headers.get("Authorization"):
            if header.startswith("Bearer"):
                return header.replace("Bearer", "").strip()
        return None

    @staticmethod
    @cache
    def _get_public_keys():
        """Return the public keys for validation"""
        LOGGER.info("Fetching AzureAD public keys")
        client_id = settings.MICROSOFT_AUTH_CLIENT_ID
        tenant_id = settings.MICROSOFT_AUTH_TENANT_ID
        url = f"https://login.microsoftonline.com/{tenant_id}/discovery/keys?appid={client_id}"

        public_keys = {}
        resp = requests.get(url, timeout=60)

        if resp.ok:
            data = resp.json()

            for jwk in data["keys"]:
                kid = jwk["kid"]
                public_keys[kid] = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(jwk))

        return public_keys
