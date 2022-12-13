"""
List of tests done on users views with a student user.
"""
import json

from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import User


class UserViewsStudentTests(TestCase):
    """
    Main tests class.
    """

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "associations_socialnetwork.json",
        "auth_group.json",
        "consents_gdprconsent.json",
        "users_associationusers.json",
        "users_gdprconsentusers.json",
        "users_user.json",
        "users_user_groups.json",
    ]

    def setUp(self):
        """
        Start a default client used on all tests, retrieves a student user.
        """
        self.student_client = Client()
        url = reverse("rest_login")
        data = {
            "username": "test@pas-unistra.fr",
            "password": "motdepasse",
        }
        self.response = self.student_client.post(url, data)

    def test_student_get_users_list(self):
        """
        GET /users/
        - A student user cannot execute this request.
        """
        response_student = self.student_client.get("/users/")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_user_detail(self):
        """
        GET /users/{id}
        - A student user cannot execute this request.
        """
        response_student = self.student_client.get("/users/2")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_patch_user_detail(self):
        """
        PATCH /users/{id}
        - A student user cannot execute this request.
        """
        response_student = self.student_client.patch(
            "/users/2", data={"username": "Bienvenueg"}, content_type="application/json"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_delete_user_detail(self):
        """
        DELETE /users/{id}
        - A student user cannot execute this request.
        """
        user_id = 2
        response_student = self.student_client.delete(f"/users/{user_id}")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_put_user_detail(self):
        """
        PUT /users/{id}
        - Request should return an error no matter which role is trying to execute it.
        """
        response_student = self.student_client.put(
            "/users/2", {"username": "Aurevoirg"}
        )
        self.assertEqual(response_student.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_get_associations_user_list(self):
        """
        GET /users/associations/
        - A student user can execute this request.
        - A student user gets correct association user list data.
        """
        response_student = self.student_client.get("/users/associations/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        associations_user_cnt = AssociationUsers.objects.filter(user_id=2).count()
        content = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(len(content), associations_user_cnt)

    def test_student_post_association_user(self):
        """
        POST /users/associations/
        - An admin-validated student user cannot execute this request.
        """
        response_student = self.student_client.post(
            "/users/associations/",
            {
                "user": "test@pas-unistra.fr",
                "association": 2,
                "has_office_status": False,
            },
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_get_associations_user_detail(self):
        """
        GET /users/associations/{user_id}
        - A student user cannot execute this request.
        """
        response_student = self.student_client.get("/users/associations/2")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_delete_user_association(self):
        """
        DELETE /users/associations/{user_id}/{association_id}
        - An student user cannot execute this request.
        """
        user_id = 2
        asso_user = AssociationUsers.objects.get(user_id=user_id)
        response_student = self.student_client.delete(
            f"/users/associations/{user_id}/{asso_user.id}"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_auth_user_detail(self):
        """
        GET /users/auth/user/
        - A student user can execute this request.
        - A student user gets correct data when executing the request.
        """
        response_student = self.student_client.get("/users/auth/user/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        user = User.objects.get(username="test@pas-unistra.fr")
        user_data = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(user_data["username"], user.username)

    def test_student_patch_auth_user_detail(self):
        """
        PATCH /users/auth/user/
        - A student user can execute this request.
        - A student user cannot update his validation status.
        - A student user cannot update his username.
        """
        user_not_valid = User.objects.get(username="test@pas-unistra.fr")
        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"is_validated_by_admin": False},
            content_type="application/json",
        )
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)
        self.assertTrue(user_not_valid.is_validated_by_admin)

        user_username = User.objects.get(username="test@pas-unistra.fr")
        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"username": "Mafoipastropmalpourlasaisong"},
            content_type="application/json",
        )
        self.assertEqual(user_username.username, "test@pas-unistra.fr")

    def test_student_put_auth_user_detail(self):
        """
        PUT /users/auth/user/
        - Request should return an error no matter which role is trying to execute it.
        """
        response_student = self.student_client.put(
            "/users/auth/user/", {"username": "Aurevoirg"}
        )
        self.assertEqual(response_student.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_get_consents_user_list(self):
        """
        GET /users/consents/
        - A student user can execute this request.
        - A student user gets only his own consents.
        """
        consents_user_cnt = GDPRConsentUsers.objects.filter(user_id=2).count()
        response_student = self.student_client.get("/users/consents/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        content = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(len(content), consents_user_cnt)

    def test_student_post_user_consents(self):
        """
        POST /users/consents/
        - A non-existing user cannot have a consent.
        - A student user can execute this request.
        - A student user cannot give the same consent twice.
        - A student user cannot give an unexisting consent.
        """
        response_student = self.student_client.post(
            "/users/consents/", {"user": "brice-de-nice-CASsé", "consent": 1}
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

        response_student = self.student_client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 1}
        )
        self.assertEqual(response_student.status_code, status.HTTP_201_CREATED)

        response_student = self.student_client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 1}
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

        response_student = self.student_client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 75}
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_get_consents_user_detail(self):
        """
        GET /users/consents/{user_id}
        - A student user cannot execute this request.
        """
        response_student = self.student_client.get("/users/consents/2")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_user_groups_list(self):
        """
        GET /users/groups/
        - A student user can execute this request.
        - A student user gets only his own groups.
        """
        response_student = self.student_client.get("/users/groups/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=2)
        groups = list(user.groups.all().values("id", "name"))
        get_groups = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(get_groups, groups)

    def test_student_post_user_groups(self):
        """
        POST /users/groups/
        - An admin-validated student user cannot execute this request.
        """
        response_student = self.student_client.post(
            "/users/groups/", {"username": "test@pas-unistra.fr", "groups": [1, 2]}
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_get_user_groups_detail(self):
        """
        GET /users/groups/{user_id}
        - A student user cannot execute this request.
        """
        response_student = self.student_client.get("/users/groups/2")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_delete_user_group(self):
        """
        DELETE /users/groups/{user_id}/{group_id}
        - A student user cannot execute this request.
        """
        user_id = 2
        response_student = self.student_client.delete(f"/users/groups/{user_id}/5")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)


class UserAuthTests(TestCase):
    """
    Special tests class.
    """

    def test_user_auth_registration(self):
        """
        POST /users/auth/registration/
        - A user can be created.
        - The same user can't be created twice.
        """
        user = {
            "email": "georges.saucisse@georgeslasaucisse.fr",
            "first_name": "Georges",
            "last_name": "La Saucisse",
        }

        response = self.client.post("/users/auth/registration/", user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post("/users/auth/registration/", user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
