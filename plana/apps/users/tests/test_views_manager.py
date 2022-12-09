"""
List of tests done on users views with a manager user.
"""
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
    """
    Main tests class.
    """

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
        """
        Start a default client used on all tests, retrieves a manager user.
        """
        self.manager_client = Client()
        url_manager = reverse("rest_login")
        data_manager = {
            "username": "gestionnaire-svu@mail.tld",
            "password": "motdepasse",
        }
        self.response = self.manager_client.post(url_manager, data_manager)

    def test_manager_get_users_list(self):
        """
        GET /users/
        - A manager user can execute this request.
        - There's at least one user in the users list.
        - We get the same amount of users through the model and through the view.
        - is_validated_by_admin query parameter only returns a non-validated user.
        """
        response_manager = self.manager_client.get("/users/")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        users_cnt = User.objects.count()
        self.assertTrue(users_cnt > 0)

        content = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(len(content), users_cnt)

        response_manager = self.manager_client.get(
            "/users/?is_validated_by_admin=false"
        )
        self.assertEqual(response_manager.data[0]["is_validated_by_admin"], False)

    def test_manager_get_user_detail(self):
        """
        GET /users/{id}
        - A manager user can execute this request.
        - User details are returned (test the "username" attribute).
        """
        response_manager = self.manager_client.get("/users/2")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=2)
        user_requested = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(user_requested["username"], user.username)

    def test_manager_patch_user_detail(self):
        """
        PATCH /users/{id}
        - A manager user can execute this request.
        - A manager user can update user details.
        - A manager user cannot update restricted CAS user details.
        """

        response_manager = self.manager_client.patch(
            "/users/2", data={"username": "Bienvenueg"}, content_type="application/json"
        )
        user = User.objects.get(pk=2)
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)
        self.assertEqual(user.username, "Bienvenueg")

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

        user_cas = User.objects.get(username="PatriciaCAS")
        self.manager_client.patch(f"/users/{user_cas.pk}", {"username": "JesuisCASg"})
        self.assertEqual(user_cas.username, "PatriciaCAS")

    def test_manager_delete_user_detail(self):
        """
        DELETE /users/{id}
        - A manager user can execute this request.
        - A user can be deleted.
        - A manager account cannot be deleted.
        """
        user_id = 2
        response = self.manager_client.delete(f"/users/{user_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(pk=user_id)

        managers_ids = [1, 4, 5]
        for manager_id in managers_ids:
            response = self.manager_client.delete(f"/users/{manager_id}")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_put_user_detail(self):
        """
        PUT /users/{id}
        - Request should return an error no matter which role is trying to execute it.
        """
        response_manager = self.manager_client.put(
            "/users/2", {"username": "Aurevoirg"}
        )
        self.assertEqual(response_manager.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_get_associations_user_list(self):
        """
        GET /users/associations/
        - A manager user can execute this request.
        - Links between user and associations are returned.
        """
        associations_user_all_cnt = AssociationUsers.objects.count()
        response_all_asso = self.manager_client.get("/users/associations/")
        content_all_asso = json.loads(response_all_asso.content.decode("utf-8"))
        self.assertEqual(response_all_asso.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content_all_asso), associations_user_all_cnt)

    def test_manager_post_association_user(self):
        """
        POST /users/associations/
        - A manager user can add an association to a validated student.
        - A manager user can add an association to a non-validated student.
        """
        response_manager = self.manager_client.post(
            "/users/associations/",
            {
                "user": "test@pas-unistra.fr",
                "association": 2,
                "has_office_status": False,
            },
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)

        response_manager = self.manager_client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
                "association": 1,
                "has_office_status": False,
            },
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)

    def test_manager_get_associations_user_detail(self):
        """
        GET /users/associations/{user_id}
        - A manager user can execute this request.
        """
        response_manager = self.manager_client.get("/users/associations/2")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        user_associations = AssociationUsers.objects.filter(user_id=2)
        user_associations_requested = json.loads(
            response_manager.content.decode("utf-8")
        )
        self.assertEqual(len(user_associations_requested), len(user_associations))

    def test_manager_delete_user_association(self):
        """
        DELETE /users/associations/{user_id}/{association_id}
        - A manager user can execute this request.
        - The link between an association and a user is deleted.
        """
        user_id = 2
        response = self.manager_client.get(f"/users/associations/{user_id}")
        first_user_association_id = response.data[0]["id"]
        response_delete = self.manager_client.delete(
            f"/users/associations/{user_id}/{str(first_user_association_id)}"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            AssociationUsers.objects.get(
                user_id=user_id, association_id=first_user_association_id
            )

    def test_manager_get_auth_user_detail(self):
        """
        GET /users/auth/user/
        - A manager user can execute this request.
        - A manager user gets correct data when executing the request.
        """
        response_manager = self.manager_client.get("/users/auth/user/")
        user = User.objects.get(username="gestionnaire-svu@mail.tld")
        user_data = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)
        self.assertEqual(user_data["username"], user.username)

    def test_manager_put_auth_user_detail(self):
        """
        PUT /users/auth/user/
        - Request should return an error no matter which role is trying to execute it.
        """
        response_manager = self.manager_client.put(
            "/users/auth/user/", {"username": "Alorsçavag"}
        )
        self.assertEqual(response_manager.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_get_consents_user_list(self):
        """
        GET /users/consents/
        - A manager user can execute this request.
        - We get the same amount of consents through the model and through the view.
        """
        consents_user_all_cnt = GDPRConsentUsers.objects.count()
        response_all_consents = self.manager_client.get("/users/consents/")
        content_all_consents = json.loads(response_all_consents.content.decode("utf-8"))
        self.assertEqual(response_all_consents.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content_all_consents), consents_user_all_cnt)

    def test_manager_get_consents_user_detail(self):
        """
        GET /users/consents/{user_id}
        - A manager user can execute this request.
        - We get the same amount of consents through the model and through the view.
        """
        response_manager = self.manager_client.get("/users/consents/2")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        user_consents = GDPRConsentUsers.objects.filter(user_id=2)
        user_consents_requested = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(len(user_consents_requested), len(user_consents))

    def test_manager_get_user_groups_list(self):
        """
        GET /users/groups/
        - A manager user can execute this request.
        - We get the same amount of groups links through the model and through the view.
        """
        response_manager = self.manager_client.get("/users/groups/")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=4)
        groups = list(user.groups.all().values("id", "name"))
        get_groups = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(get_groups, groups)

    def test_manager_post_group_user(self):
        """
        POST /users/group/
        - A manager user can add a group to a validated student.
        - A manager user can add a group to a non-validated student.
        """
        response_manager = self.manager_client.post(
            "/users/groups/",
            {"username": "test@pas-unistra.fr", "groups": [1, 2]},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        response_manager = self.manager_client.post(
            "/users/groups/",
            {"username": "prenom.nom@adressemail.fr", "groups": [1, 2]},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

    def test_manager_get_user_groups_detail(self):
        """
        GET /users/groups/{user_id}
        - A manager user can execute this request.
        - We get the same amount of groups links through the model and through the view.
        """
        response_manager = self.manager_client.get("/users/groups/2")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=2)
        groups = list(user.groups.all().values("id", "name"))
        get_groups = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(get_groups, groups)

    def test_manager_delete_user_group(self):
        """
        DELETE /users/groups/{user_id}/{group_id}
        - A manager user can execute this request.
        - The link between a group and a user is deleted.
        - A user should have at least one group.
        """
        user_id = 8
        response = self.manager_client.get(f"/users/groups/{user_id}")
        first_user_group_id = response.data[0]["id"]
        second_user_group_id = response.data[1]["id"]
        first_response_delete = self.manager_client.delete(
            f"/users/groups/{user_id}/{str(first_user_group_id)}"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        second_response_delete = self.manager_client.delete(
            f"/users/groups/{user_id}/{str(second_user_group_id)}"
        )
        self.assertEqual(
            second_response_delete.status_code, status.HTTP_400_BAD_REQUEST
        )
