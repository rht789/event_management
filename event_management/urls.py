from django.contrib import admin
from django.urls import include, path
from debug_toolbar.toolbar import debug_toolbar_urls
from core.views import no_permission
from events.views import home

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name='home'),
    path("no_permission", no_permission, name='no-permission'),
    path("events/", include("events.urls")),
    path("users/", include("users.urls")),
] + debug_toolbar_urls()