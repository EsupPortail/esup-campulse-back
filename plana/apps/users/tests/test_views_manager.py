import json

from django.core.exceptions import ObjectDoesNotExist
from django.test import TestCase, Client
from django.urls import reverse

from allauth.socialaccount.models import SocialAccount
from rest_framework import status

from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import User
from plana.apps.users.provider import CASProvider


class UserViewsManagerTests(TestCase):
    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "associations_socialnetwork.json",
        "account_emailaddress.json",
        "consents_gdprconsent.json",
        "auth_group.json",
        "users_associationusers.json",
        "users_gdprconsentusers.json",
        "users_user.json",
        "users_user_groups.json",
    ]

    def setUp(self):
        self.manager_client = Client()
        url_manager = reverse("rest_login")
        data_manager = {
            "username": "gestionnaire-svu@mail.tld",
            "password": "motdepasse",
        }
        self.response = self.manager_client.post(url_manager, data_manager)

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

    def test_manager_get_users_list(self):
        users_cnt = User.objects.count()
        self.assertTrue(users_cnt > 0)

        # A manager user can execute this request
        response_manager = self.manager_client.get("/users/")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        # A manager user gets a list of all users in db
        content = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(len(content), users_cnt)

        # Get only users not validated by an admin.
        response_manager = self.manager_client.get(
            "/users/?is_validated_by_admin=false"
        )
        self.assertEqual(response_manager.data[0]["is_validated_by_admin"], False)

    def test_manager_get_user_detail(self):
        # A manager user can execute this request
        response_manager = self.manager_client.get("/users/2")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        # A manager user gets informations of requested user
        user = User.objects.get(pk=2)
        user_requested = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(user_requested["username"], user.username)

    def test_manager_patch_user_detail(self):
        # A manager user can execute this request and modifications are correctly applied on local account
        response_manager = self.manager_client.patch(
            "/users/2", data={"username": "Bienvenueg"}, content_type="application/json"
        )
        user = User.objects.get(pk=2)
        self.assertEqual(user.username, "Bienvenueg")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        # Some CAS user fields cannot be modified
        user_cas = User.objects.get(username="PatriciaCAS")
        response = self.manager_client.patch(
            f"/users/{user_cas.pk}", {"username": "JesuisCASg"}
        )
        self.assertEqual(user_cas.username, "PatriciaCAS")

    def test_manager_delete_user_detail(self):
        # A manager can delete a user.
        user_id = 2
        response = self.manager_client.delete(f"/users/{user_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist) as ctx:
            User.objects.get(pk=user_id)

        # A manager cannot delete another manager.
        managers_ids = [1, 4, 5]
        for manager_id in managers_ids:
            response = self.manager_client.delete(f"/users/{manager_id}")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_put_user_detail_unexisting(self):
        # Request should return an error 404 no matter which role is trying to execute it
        response_manager = self.manager_client.put(
            "/users/2", {"username": "Aurevoirg"}
        )
        self.assertEqual(response_manager.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_get_auth_user_detail(self):
        # An authenticated manager get correct data when executing the request
        response_manager = self.manager_client.get("/users/auth/user/")
        user = User.objects.get(username="gestionnaire-svu@mail.tld")
        user_data = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(user_data["username"], user.username)

    def test_manager_patch_auth_user_detail(self):
        # PUT request is never accessible for authenticated users, returns 404
        response = self.manager_client.put(
            "/users/auth/user/", {"username": "Alorsçavag"}
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_get_associations_user_list(self):
        # A manager user can execute this request
        response = self.manager_client.get("/users/associations/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_get_self_associations_user_list(self):
        # A manager user can get a list of every association-user links
        associations_user_all_cnt = AssociationUsers.objects.count()
        response_all_asso = self.manager_client.get("/users/associations/")
        content_all_asso = json.loads(response_all_asso.content.decode("utf-8"))
        self.assertEqual(len(content_all_asso), associations_user_all_cnt)

    def test_manager_delete_user_association(self):
        # A manager user can execute this request.
        user_id = 2
        response = self.manager_client.get(f"/users/associations/{user_id}")
        first_user_association_id = response.data[0]["id"]
        response_delete = self.manager_client.delete(
            f"/users/associations/{user_id}/{str(first_user_association_id)}"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist) as ctx:
            AssociationUsers.objects.get(
                user_id=user_id, association_id=first_user_association_id
            )

    def test_manager_get_consents_user_list(self):
        # A manager user can execute this request
        response = self.manager_client.get("/users/consents/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_manager_get_self_consents_user_list(self):
        # A manager user can get a list of every regulation consented by every user
        consents_user_all_cnt = GDPRConsentUsers.objects.count()
        response_all_consents = self.manager_client.get("/users/consents/")
        content_all_consents = json.loads(response_all_consents.content.decode("utf-8"))
        self.assertEqual(len(content_all_consents), consents_user_all_cnt)

    def test_manager_get_user_groups_list(self):
        # A manager user can execute this request
        response_manager = self.manager_client.get("/users/groups/2")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        # A manager user get correctly all groups linked to a chosen user
        user = User.objects.get(pk=2)
        groups = list(user.groups.all().values("id", "name"))
        get_groups = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(get_groups, groups)

    def test_manager_get_self_user_groups_list(self):
        # A manager user can execute this request
        response_manager = self.manager_client.get("/users/groups/")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        # An authenticated user get correctly all his groups even if manager
        user = User.objects.get(pk=4)
        groups = list(user.groups.all().values("id", "name"))
        get_groups = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(get_groups, groups)

    def test_manager_delete_user_group(self):
        # A manager user can execute this request.
        user_id = 8
        response = self.manager_client.get(f"/users/groups/{user_id}")
        first_user_group_id = response.data[0]["id"]
        second_user_group_id = response.data[1]["id"]
        first_response_delete = self.manager_client.delete(
            f"/users/groups/{user_id}/{str(first_user_group_id)}"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        # A user should have at least one group.
        second_response_delete = self.manager_client.delete(
            f"/users/groups/{user_id}/{str(second_user_group_id)}"
        )
        self.assertEqual(
            second_response_delete.status_code, status.HTTP_400_BAD_REQUEST
        )
