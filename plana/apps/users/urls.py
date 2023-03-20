"""List of URLs linked to operations that can be done on users and users related models."""
from django.conf import settings
from django.urls import include, path, re_path

from .views.association_users import (
    AssociationUsersListCreate,
    AssociationUsersRetrieve,
    AssociationUsersUpdateDestroy,
)
from .views.cas import CASLogin, CASLogout, cas_test, cas_verify
from .views.external import ExternalUserRetrieve

# from .views.gdpr_consent_users import UserConsentsListCreate, UserConsentsRetrieve
from .views.user import UserListCreate, UserRetrieveUpdateDestroy
from .views.user_auth import PasswordResetConfirm, UserAuthVerifyEmailView, UserAuthView
from .views.user_groups_institutions_commissions import (
    UserGroupsInstitutionsCommissionsDestroy,
    UserGroupsInstitutionsCommissionsDestroyWithCommission,
    UserGroupsInstitutionsCommissionsListCreate,
    UserGroupsInstitutionsCommissionsRetrieve,
)

urlpatterns = [
    path(
        "associations/",
        AssociationUsersListCreate.as_view(),
        name="user_associations_list_create",
    ),
    path(
        "<int:user_id>/associations/",
        AssociationUsersRetrieve.as_view(),
        name="user_associations_retrieve",
    ),
    path(
        "<int:user_id>/associations/<int:association_id>",
        AssociationUsersUpdateDestroy.as_view(),
        name="user_associations_update_destroy",
    ),
    path("auth/cas/login/", CASLogin.as_view(), name="rest_cas_login"),
    path("auth/cas/logout/", CASLogout.as_view(), name="rest_cas_logout"),
    path("auth/user/", UserAuthView.as_view(), name="rest_user_details"),
    path("auth/", include("dj_rest_auth.urls")),
    re_path(
        r"auth/password/reset/confirm/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,32})/$",
        PasswordResetConfirm.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "auth/registration/verify-email/",
        UserAuthVerifyEmailView.as_view(),
        name="rest_verify_email",
    ),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
    # path("consents/", UserConsentsListCreate.as_view(), name="user_consents_list_create"),
    # path("consents/<int:user_id>", UserConsentsRetrieve.as_view(), name="user_consents_retrieve",),
    path("", UserListCreate.as_view(), name="user_list_create"),
    path("<int:pk>", UserRetrieveUpdateDestroy.as_view(), name="user_detail"),
    path(
        "groups/",
        UserGroupsInstitutionsCommissionsListCreate.as_view(),
        name="user_groups_institutions_commissions_list_create",
    ),
    path(
        "<int:user_id>/groups/",
        UserGroupsInstitutionsCommissionsRetrieve.as_view(),
        name="user_groups_institutions_commissions_retrieve",
    ),
    path(
        "<int:user_id>/groups/<int:group_id>",
        UserGroupsInstitutionsCommissionsDestroy.as_view(),
        name="user_groups_institutions_commissions_destroy",
    ),
    path(
        "<int:user_id>/groups/<int:group_id>/commissions/<int:commission_id>",
        UserGroupsInstitutionsCommissionsDestroyWithCommission.as_view(),
        name="user_groups_institutions_commissions_destroy_with_commission",
    ),
    path(
        "external/",
        ExternalUserRetrieve.as_view(),
        name="external_user_retrieve",
    ),
]

if settings.DEBUG:  # pragma: no cover
    urlpatterns += [
        path("auth/cas_test/", cas_test, name="cas_test"),
        path("auth/cas_verify/", cas_verify, name="cas_verify"),
    ]
