from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.http import JsonResponse
from django.urls import path, include

from app.views import IndexView, status


urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("microsoft/", include("microsoft_auth.urls", namespace="microsoft")),
    path("status/", status, name="status"),
    path("", IndexView.as_view(), name="index"),
]
