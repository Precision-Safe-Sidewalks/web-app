import re

from django.conf import settings
from django.http import HttpResponseRedirect
from django.urls import reverse


class AuthMiddleware:
    """Middleware to programatically check user authentication"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        """Pre-process the request to check if auth is required"""
        if self.is_public(request.path):
            return self.get_response(request)

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
