from django.conf import settings
from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path("<int:pk>", views.UserDetail.as_view(), name="user_detail"),
    path("", views.UserList.as_view(), name="user_list"),
    path("association/", views.AssociationUsersList.as_view(), name="asso_users_list"),
    path("groups/", views.GroupList.as_view(), name="group_list"),
    path("auth/cas/login/", views.CASLogin.as_view(), name="rest_cas_login"),
    path("auth/cas/logout/", views.CASLogout.as_view(), name="rest_cas_logout"),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    re_path(
        "auth/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$",
        views.PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
]

if settings.DEBUG:
    urlpatterns += [
        path("auth/cas_test/", views.cas_test, name="cas_test"),
        path("auth/cas_verify/", views.cas_verify, name="cas_verify"),
    ]
