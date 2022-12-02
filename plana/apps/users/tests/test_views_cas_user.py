import json

from django.test import TestCase, Client
from django.urls import reverse

from allauth.socialaccount.models import SocialAccount
from rest_framework import status

from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import User
from plana.apps.users.provider import CASProvider


class UserViewsTests(TestCase):
    #    fixtures = [
    #        "associations_activityfield.json",
    #        "associations_association.json",
    #        "associations_institution.json",
    #        "associations_institutioncomponent.json",
    #        "associations_socialnetwork.json",
    #        "account_emailaddress.json",
    #        "consents_gdprconsent.json",
    #        "auth_group.json",
    #        "users_associationusers.json",
    #        "users_gdprconsentusers.json",
    #        "users_user.json",
    #        "users_user_groups.json",
    #    ]

    def setUp(self):
        user = User.objects.create_user(
            username="PatriciaCAS",
            password="pbkdf2_sha256$260000$H2vwf1hYXyooB1Qhsevrk6$ISSNgBZtbGWwNL6TSktlDCeGfd5Ib9F3c9DkKhYkZMQ=",
            email="test@unistra.fr",
        )
        SocialAccount.objects.create(
            user=user,
            provider=CASProvider.id,
            uid=user.username,
            extra_data={},
        )
        self.cas_client = Client()
        url_cas = reverse("rest_login")
        data_cas = {
            "username": "PatriciaCAS",
            "password": "motdepasse",
        }
        self.response = self.cas_client.post(url_cas, data_cas)

    # TODO : review this test : bad status code returned


#    def test_cas_patch_auth_user_detail(self):
#        # A CAS user can execute this request but cannot update some CAS fields from his account
#        user_cas = User.objects.get(username="PatriciaCAS")
#        response_not_modified = self.cas_client.patch(
#            "/users/auth/user/", {"username": "JesuisCASg"}
#        )
#        self.assertEqual(user_cas.username, "PatriciaCAS")
#        self.assertEqual(response.status_code, status.HTTP_200_OK)
