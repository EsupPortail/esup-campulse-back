"""List of URLs linked to operations that can be done on users and users related models."""

from django.conf import settings
from django.urls import include, path, re_path

from .views.association_user import (
    AssociationUserListCreate,
    AssociationUserRetrieve,
    AssociationUserUpdateDestroy,
)
from .views.cas import CASLogin, CASLogout, cas_test, cas_verify
from .views.external import ExternalUserList
from .views.group_institution_fund_user import (
    GroupInstitutionFundUserDestroy,
    GroupInstitutionFundUserDestroyWithFund,
    GroupInstitutionFundUserDestroyWithInstitution,
    GroupInstitutionFundUserListCreate,
    GroupInstitutionFundUserRetrieve,
)
from .views.user import UserListCreate, UserRetrieveUpdateDestroy
from .views.user_auth import PasswordResetConfirm, UserAuthVerifyEmailView, UserAuthView

urlpatterns = [
    path("", UserListCreate.as_view(), name="user_list_create"),
    path("<int:pk>", UserRetrieveUpdateDestroy.as_view(), name="user_detail"),
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
    path(
        "associations/",
        AssociationUserListCreate.as_view(),
        name="association_user_list_create",
    ),
    path(
        "<int:user_id>/associations/",
        AssociationUserRetrieve.as_view(),
        name="association_user_retrieve",
    ),
    path(
        "<int:user_id>/associations/<int:association_id>",
        AssociationUserUpdateDestroy.as_view(),
        name="association_user_update_destroy",
    ),
    path(
        "groups/",
        GroupInstitutionFundUserListCreate.as_view(),
        name="group_institution_fund_user_list_create",
    ),
    path(
        "<int:user_id>/groups/",
        GroupInstitutionFundUserRetrieve.as_view(),
        name="group_institution_fund_user_retrieve",
    ),
    path(
        "<int:user_id>/groups/<int:group_id>",
        GroupInstitutionFundUserDestroy.as_view(),
        name="group_institution_fund_user_destroy",
    ),
    path(
        "<int:user_id>/groups/<int:group_id>/funds/<int:fund_id>",
        GroupInstitutionFundUserDestroyWithFund.as_view(),
        name="group_institution_fund_user_destroy_with_fund",
    ),
    path(
        "<int:user_id>/groups/<int:group_id>/institutions/<int:institution_id>",
        GroupInstitutionFundUserDestroyWithInstitution.as_view(),
        name="group_institution_fund_user_destroy_with_institution",
    ),
]

if settings.LDAP_ENABLED is True:
    urlpatterns += [
        path("external/", ExternalUserList.as_view(), name="external_user_list"),
    ]

if settings.DEBUG:  # pragma: no cover
    urlpatterns += [
        path("auth/cas_test/", cas_test, name="cas_test"),
        path("auth/cas_verify/", cas_verify, name="cas_verify"),
    ]
