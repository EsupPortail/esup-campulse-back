"""
List of root URLs, some linking to subapps.
"""
from django.conf import settings
from django.urls import include, path
from django.contrib import admin

from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

from .views import home

admin.autodiscover()

urlpatterns = [
    path("", home, name="home"),
    path("associations/", include("plana.apps.associations.urls")),
    path("consents/", include("plana.apps.consents.urls")),
    path("groups/", include("plana.apps.groups.urls")),
    path("users/", include("plana.apps.users.urls")),
    path("admin/", admin.site.urls),
    path(
        "api/schema/", SpectacularAPIView.as_view(), name="schema"
    ),  # Downloads schema.yml
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]

# debug toolbar for dev
if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
