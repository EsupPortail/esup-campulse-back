from django.conf import settings
from django.urls import include, path, re_path

from .views.user import (
    UserList,
    UserDetail,
    AssociationUsersList,
    CASLogin,
    CASLogout,
    PasswordResetConfirm,
    GroupList,
    cas_test,
    cas_verify,
)

urlpatterns = [
    path("", UserList.as_view(), name="user_list"),
    path("<int:pk>", UserDetail.as_view(), name="user_detail"),
    path("association/", AssociationUsersList.as_view(), name="asso_users_list"),
    path("auth/cas/login/", CASLogin.as_view(), name="rest_cas_login"),
    path("auth/cas/logout/", CASLogout.as_view(), name="rest_cas_logout"),
    path("auth/", include("dj_rest_auth.urls")),
    re_path(
        "auth/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$",
        PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("groups/", GroupList.as_view(), name="group_list"),
]

if settings.DEBUG:
    urlpatterns += [
        path("auth/cas_test/", cas_test, name="cas_test"),
        path("auth/cas_verify/", cas_verify, name="cas_verify"),
    ]
