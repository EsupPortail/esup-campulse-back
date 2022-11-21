from django.conf import settings
from django.urls import include, path, re_path

from .views.user import (
    UserDetail,
    UserAssociationsCreate,
    UserAssociationsList,
    UserGroupsCreate,
    UserGroupsList,
    CASLogin,
    CASLogout,
    PasswordResetView,
    PasswordResetConfirm,
    cas_test,
    cas_verify,
)

urlpatterns = [
    path("<int:pk>", UserDetail.as_view(), name="user_detail"),
    path(
        "associations/",
        UserAssociationsCreate.as_view(),
        name="user_associations_create",
    ),
    path(
        "associations/<int:pk>",
        UserAssociationsList.as_view(),
        name="user_associations_list",
    ),
    path("groups/", UserGroupsCreate.as_view(), name="user_groups_create"),
    path("groups/<int:pk>", UserGroupsList.as_view(), name="user_groups_list"),
    path("auth/cas/login/", CASLogin.as_view(), name="rest_cas_login"),
    path("auth/cas/logout/", CASLogout.as_view(), name="rest_cas_logout"),
    path(
        "auth/password/reset/", PasswordResetView.as_view(), name="rest_password_reset"
    ),
    path("auth/", include("dj_rest_auth.urls")),
    re_path(
        "auth/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$",
        PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("auth/cas_test/", cas_test, name="cas_test"),
        path("auth/cas_verify/", cas_verify, name="cas_verify"),
    ]
