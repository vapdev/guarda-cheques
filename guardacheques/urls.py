from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.views.generic import RedirectView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("django.contrib.auth.urls")),
    path("cheques/", include("cheques.urls")),
    path("", RedirectView.as_view(pattern_name="index", permanent=True)),
]
