"""List of tests done on users views with a CAS user."""

from unittest.mock import patch

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.core import mail
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from rest_framework import status

from plana.apps.users.models.user import AssociationUser, User
from plana.apps.users.provider import CASProvider


class UserViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "tests/commissions_fund.json",
        "tests/contents_setting.json",
        "tests/institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "users_associationuser.json",
        "users_groupinstitutionfunduser.json",
        "users_user.json",
    ]

    @patch('plana.apps.users.serializers.cas.CASSerializer.validate')
    @override_settings(CAS_AUTHORIZED_SERVICES=["http://service.url"])
    def setUp(self, validate):
        """Fake account to test CAS."""
        user = User.objects.create_user(
            username="PatriciaCAS",
            password="pbkdf2_sha256$260000$H2vwf1hYXyooB1Qhsevrk6$ISSNgBZtbGWwNL6TSktlDCeGfd5Ib9F3c9DkKhYkZMQ=",
            email="patriciacas@unistra.fr",
            is_validated_by_admin=False,
        )
        SocialAccount.objects.create(
            user=user,
            provider=CASProvider.id,
            uid=user.username,
            extra_data={},
        )
        EmailAddress.objects.create(
            user=user,
            email="patriciacas@unistra.fr",
            verified=True,
            primary=True,
        )
        validate.return_value = {
            "ticket": "aaa",
            "service": "http://service.url",
            "user": User.objects.get(username="PatriciaCAS"),
        }
        self.cas_client = Client()
        url_cas = reverse("rest_cas_login")
        data_cas = {
            "username": "PatriciaCAS",
            "password": "motdepasse",
            "ticket": "aaa",
            "service": "http://service.url",
        }
        self.response = self.cas_client.post(url_cas, data_cas)

    def test_cas_patch_auth_user_detail(self):
        """A CAS user can execute this request but cannot update CAS fields from his account."""
        user_cas = User.objects.get(username="PatriciaCAS")
        self.assertFalse(len(mail.outbox))
        response_not_modified = self.cas_client.patch(
            "/users/auth/user/",
            data={"email": "george-lucas@unistra.fr"},
            content_type="application/json",
        )
        self.assertTrue(len(mail.outbox))
        self.assertEqual(user_cas.email, "patriciacas@unistra.fr")
        self.assertEqual(response_not_modified.status_code, status.HTTP_200_OK)

        AssociationUser.objects.create(user_id=user_cas.pk, association_id=1)
        response_not_modified = self.cas_client.patch(
            "/users/auth/user/",
            data={"email": "george-lucas@unistra.fr"},
            content_type="application/json",
        )
