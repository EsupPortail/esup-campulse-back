"""List of root URLs, some linking to subapps."""
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)
from rest_framework.exceptions import bad_request, server_error

from .views import forbidden, not_found, ok

admin.autodiscover()

handler400 = bad_request
handler403 = forbidden
handler404 = not_found
handler500 = server_error

urlpatterns = [
    path("", ok, name="home"),
    # re_path(r'^media/(?P<path>.*)$', serve, kwargs={'document_root': settings.MEDIA_ROOT}),
    path("associations/", include("plana.apps.associations.urls")),
    path("commissions/", include("plana.apps.commissions.urls")),
    path("contents/", include("plana.apps.contents.urls")),
    path("documents/", include("plana.apps.documents.urls")),
    path("groups/", include("plana.apps.groups.urls")),
    path("institutions/", include("plana.apps.institutions.urls")),
    path("projects/", include("plana.apps.projects.urls")),
    path("users/", include("plana.apps.users.urls")),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),  # Downloads schema.yml
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
    path("summernote/", include('django_summernote.urls')),
    path("mail_template/", include('plana.libs.mail_template.urls')),
    path("_hc/", include('health_check.urls')),
]

# debug toolbar for dev
if settings.DEBUG and "debug_toolbar" in settings.INSTALLED_APPS:  # pragma: no cover
    import debug_toolbar

    urlpatterns += [
        path("__debug__/", include(debug_toolbar.urls)),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
