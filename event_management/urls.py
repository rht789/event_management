from django.contrib import admin
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls
from core.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name='main_home'),
    path("events/", include("events.urls")),
    path("users/", include("users.urls")),
] + debug_toolbar_urls()