from django.contrib import admin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import include, path

from app.views import status

urlpatterns = [
    path("admin/", admin.site.urls),
    path("auth/login/", LoginView.as_view(), name="login"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("microsoft/", include("microsoft_auth.urls", namespace="microsoft")),
    path("status/", status, name="status"),
    path("api/", include("api.urls")),
    path("", include("pages.urls")),
]
