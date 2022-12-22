"""
List of tests done on users views with a CAS user.
"""
from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.test import Client, TestCase
from django.urls import reverse

from plana.apps.users.models.user import User
from plana.apps.users.provider import CASProvider


class UserViewsTests(TestCase):
    """
    Main tests class.
    """

    def setUp(self):
        user = User.objects.create_user(
            username="PatriciaCAS",
            password="pbkdf2_sha256$260000$H2vwf1hYXyooB1Qhsevrk6$ISSNgBZtbGWwNL6TSktlDCeGfd5Ib9F3c9DkKhYkZMQ=",
            email="test@unistra.fr",
            is_validated_by_admin=True,
        )
        SocialAccount.objects.create(
            user=user,
            provider=CASProvider.id,
            uid=user.username,
            extra_data={},
        )
        EmailAddress.objects.create(
            user=user,
            email="test@unistra.fr",
            verified=True,
            primary=True,
        )
        self.cas_client = Client()
        url_cas = reverse("rest_login")
        data_cas = {
            "username": "PatriciaCAS",
            "password": "motdepasse",
        }
        self.response = self.cas_client.post(url_cas, data_cas)
        print(self.response.data)

    # TODO Rewrite user CAS test login.
    # def test_cas_patch_auth_user_detail(self):
    #    """
    #    A CAS user can execute this request but cannot update some CAS fields from his account.
    #    """
    #    user_cas = User.objects.get(username="PatriciaCAS")
    #    response_not_modified = self.cas_client.patch(
    #        "/users/auth/user/", {"username": "GeorgeLuCAS"}
    #    )
    #    self.assertEqual(user_cas.username, "PatriciaCAS")
    #    self.assertEqual(response_not_modified.status_code, status.HTTP_200_OK)
