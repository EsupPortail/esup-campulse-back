import json

from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import User


class UserViewsStudentTests(TestCase):
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
        self.client = Client()
        url = reverse("rest_login")
        data = {
            "username": "test@pas-unistra.fr",
            "password": "motdepasse",
        }
        self.response = self.client.post(url, data)

    def test_student_get_users_list(self):
        # A student user cannot execute this request
        response = self.client.get("/users/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_user_detail(self):
        # A student user cannot execute this request
        response = self.client.get("/users/2")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_patch_user_detail(self):
        # A student user cannot execute this request
        response_student = self.client.patch(
            "/users/2", data={"username": "Bienvenueg"}, content_type="application/json"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_put_user_detail_unexisting(self):
        # Request should return an error 404 no matter which role is trying to execute it
        response_student = self.client.put("/users/2", {"username": "Aurevoirg"})
        self.assertEqual(response_student.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_get_auth_user_detail(self):
        # An authenticated user can get execute this request
        response = self.client.get("/users/auth/user/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # An authenticated user get correct data when executing the request
        user = User.objects.get(username="test@pas-unistra.fr")
        user_data = json.loads(response.content.decode("utf-8"))
        self.assertEqual(user_data["username"], user.username)

    def test_student_patch_auth_user_detail(self):
        # PUT request is never accessible for authenticated users, returns 404
        response = self.client.put("/users/auth/user/", {"username": "Alorsçavag"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # A student user cannot update his validation status
        user_not_valid = User.objects.get(username="test@pas-unistra.fr")
        response = self.client.patch(
            "/users/auth/user/",
            data={"is_validated_by_admin": False},
            content_type="application/json",
        )
        self.assertTrue(user_not_valid.is_validated_by_admin)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # A student user cannot update his username
        user_username = User.objects.get(username="test@pas-unistra.fr")
        response = self.client.patch(
            "/users/auth/user/",
            data={"username": "Mafoipastropmalpourlasaisong"},
            content_type="application/json",
        )
        self.assertEqual(user_username.username, "test@pas-unistra.fr")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_get_associations_user_list(self):
        # A student user can't execute this request.
        response = self.client.get("/users/associations/2")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_self_associations_user_list(self):
        # A student user can execute this request.
        response_student = self.client.get("/users/associations/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        # A student user gets correct association user list data
        associations_user_cnt = AssociationUsers.objects.filter(user_id=2).count()
        content = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(len(content), associations_user_cnt)

    def test_student_link_validated_user_to_associations(self):
        # An admin-validated user can't be added in an association
        response = self.client.post(
            "/users/associations/",
            {
                "user": "test@pas-unistra.fr",
                "association": 2,
                "has_office_status": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_link_user_to_associations(self):
        # A non-validated user can be added in an association
        response = self.client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
                "association": 1,
                "has_office_status": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # A user cannot be added twice in the same association
        response = self.client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
                "association": 1,
                "has_office_status": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_link_user_to_associations_non_existing(self):
        # A user cannot be part of a non-existing association
        response = self.client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
                "association": 99,
                "has_office_status": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_delete_user_association(self):
        # A student user can't execute this request.
        asso_user = AssociationUsers.objects.get(user_id=2)
        response = self.client.delete(f"/users/associations/{asso_user.id}")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_consents_user_list(self):
        # A student user can't execute this request.
        response = self.client.get("/users/consents/2")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_self_consents_user_list(self):
        # A student user can execute this request and get only his consents
        consents_user_cnt = GDPRConsentUsers.objects.filter(user_id=2).count()
        response_student = self.client.get("/users/consents/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        content_student = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(len(content_student), consents_user_cnt)

    def test_student_post_user_consents(self):
        # An authenticated user can execute this request
        response = self.client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # A user can't consent mutliple times to the same regulation
        response = self.client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_post_user_consents_non_existing(self):
        # A user cannot consent to non-existing gdpr-consent object
        response = self.client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 75}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_get_user_groups_list(self):
        # A student user can't execute this request
        response_student = self.client.get("/users/groups/2")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_self_user_groups_list(self):
        # A student user can execute this request and get correctly all his groups
        response_student = self.client.get("/users/groups/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=2)
        groups = list(user.groups.all().values("id", "name"))
        get_groups = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(get_groups, groups)

    def test_student_link_validated_user_to_groups(self):
        # Groups of admin-validated accounts can't be updated
        response = self.client.post(
            "/users/groups/", {"username": "test@pas-unistra.fr", "groups": [1, 2]}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_link_non_validated_user_to_groups(self):
        # Groups of non-validated accounts can be updated
        response = self.client.post(
            "/users/groups/",
            {"username": "prenom.nom@adressemail.fr", "groups": [1, 2]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_student_link_user_to_groups_non_existing(self):
        # Cannot add a user in a non-existing group
        response = self.client.post(
            "/users/groups/", {"username": "prenom.nom@adressemail.fr", "groups": [66]}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAuthTests(TestCase):
    def test_user_auth_registration(self):
        user = {
            "email": "georges.saucisse@georgeslasaucisse.fr",
            "first_name": "Georges",
            "last_name": "La Saucisse",
        }

        # It is possible to create users
        response = self.client.post("/users/auth/registration/", user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # It is not possible to create the same user twice
        response = self.client.post("/users/auth/registration/", user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
