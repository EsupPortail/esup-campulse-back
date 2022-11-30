from django.conf import settings
from django.urls import include, path, re_path

from .views.association_users import AssociationUsersListCreate, AssociationUsersRetrieve
from .views.cas import CASLogin, CASLogout, cas_test, cas_verify
from .views.gdpr_consent_users import UserConsentsCreate, UserConsentsList

from .views.user import PasswordResetConfirm, UserDetailsView  # , UserList, UserDetail
from .views.user_groups import UserGroupsCreate, UserGroupsList

urlpatterns = [
    path(
        "associations/",
        AssociationUsersListCreate.as_view(),
        name="user_associations_create",
    ),
    path(
        "associations/<int:pk>",
        AssociationUsersRetrieve.as_view(),
        name="user_associations_list",
    ),
    path("auth/cas/login/", CASLogin.as_view(), name="rest_cas_login"),
    path("auth/cas/logout/", CASLogout.as_view(), name="rest_cas_logout"),
    path("auth/user/", UserDetailsView.as_view(), name="rest_user_details"),
    path("auth/", include("dj_rest_auth.urls")),
    re_path(
        "auth/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$",
        PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    path("consents/", UserConsentsCreate.as_view(), name="user_consents_create"),
    path("consents/<int:pk>", UserConsentsList.as_view(), name="user_consents_list"),
    # path("", UserList.as_view(), name="user_list"),
    # path("<int:pk>", UserDetail.as_view(), name="user_detail"),
    path("groups/", UserGroupsCreate.as_view(), name="user_groups_create"),
    path("groups/<int:pk>", UserGroupsList.as_view(), name="user_groups_list"),
]

if settings.DEBUG:  # pragma: no cover
    urlpatterns += [
        path("auth/cas_test/", cas_test, name="cas_test"),
        path("auth/cas_verify/", cas_verify, name="cas_verify"),
    ]
