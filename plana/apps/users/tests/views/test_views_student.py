"""List of tests done on users views with a student user."""
import json

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.users.models.user import User


class UserViewsStudentTests(TestCase):
    """Main tests class."""

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_commission.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "users_associationuser.json",
        "users_groupinstitutioncommissionuser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Clients used on all tests (simple student user, president of an association)."""
        cls.unvalidated_user_id = 2
        cls.unvalidated_user_name = "compte-non-valide@mail.tld"

        cls.student_user_id = 11
        cls.student_user_name = "etudiant-asso-site@mail.tld"
        cls.student_client = Client()
        url = reverse("rest_login")
        data = {
            "username": cls.student_user_name,
            "password": "motdepasse",
        }
        cls.response_student = cls.student_client.post(url, data)

        cls.president_user_id = 13
        cls.president_user_name = "president-asso-site@mail.tld"
        cls.president_student_client = Client()
        url = reverse("rest_login")
        data = {
            "username": cls.president_user_name,
            "password": "motdepasse",
        }
        cls.response_president = cls.president_student_client.post(url, data)

    def test_student_get_auth_user_detail(self):
        """
        GET /users/auth/user/ .

        - A student user can execute this request.
        - A student user gets correct data when executing the request.
        """
        response_student = self.student_client.get("/users/auth/user/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        user = User.objects.get(username=self.student_user_name)
        user_data = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(user_data["username"], user.username)

    def test_student_patch_auth_user_detail(self):
        """
        PATCH /users/auth/user/ .

        - A student user can execute this request.
        - A student user cannot update his validation status.
        - A student user cannot update his username.
        - A student user cannot update his permission to submit projects.
        - A student user cannot update his email address with an address from another account.
        - A student user can update his email address.
        - Updating the email address doesn't change the username without validation.
        """
        student_user = User.objects.get(username=self.student_user_name)
        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"is_validated_by_admin": False},
            content_type="application/json",
        )
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)
        self.assertTrue(student_user.is_validated_by_admin)

        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"username": "Mafoipastropmalpourlasaisong"},
            content_type="application/json",
        )
        student_user = User.objects.get(username=self.student_user_name)
        self.assertEqual(student_user.username, self.student_user_name)

        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"can_submit_projects": False},
            content_type="application/json",
        )
        student_user = User.objects.get(username=self.student_user_name)
        self.assertTrue(student_user.can_submit_projects)

        new_email = self.president_user_name
        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"email": new_email},
            content_type="application/json",
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

        new_email = f"mon-esprit-est-mortadelle@{settings.RESTRICTED_DOMAINS[0]}"
        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"email": new_email},
            content_type="application/json",
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

        new_email = "cle-a-molette@ok-motors.com"
        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"email": new_email},
            content_type="application/json",
        )
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)
        student_user = User.objects.get(email=new_email)
        self.assertEqual(student_user.email, new_email)
        self.assertEqual(student_user.username, new_email)

    def test_student_put_auth_user_detail(self):
        """
        PUT /users/auth/user/ .

        - Request should return an error no matter which role is trying to execute it.
        """
        response_student = self.student_client.put(
            "/users/auth/user/", {"username": "Aurevoirg"}
        )
        self.assertEqual(
            response_student.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_student_delete_auth_user(self):
        """
        DELETE /users/auth/user/ .

        - A user should be able to delete his own account.
        """
        response_student = self.student_client.delete("/users/auth/user/")
        student_user_query = User.objects.filter(username=self.student_user_name)
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)
        self.assertEqual(len(student_user_query), 0)

    def test_student_get_user_groups_list(self):
        """
        GET /users/groups/ .

        - A student user can execute this request.
        """
        response_student = self.student_client.get("/users/groups/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

    def test_student_post_user_groups(self):
        """
        POST /users/groups/ .

        - An admin-validated student user cannot execute this request.
        """
        response_student = self.student_client.post(
            "/users/groups/", {"username": self.student_user_name, "group": 6}
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_user_groups_detail(self):
        """
        GET /users/{user_id}/groups/ .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.get(
            f"/users/{self.student_user_id}/groups/"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_delete_user_group(self):
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.delete(
            f"/users/{self.student_user_id}/groups/6"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)


class UserAuthTests(TestCase):
    """Special tests class."""

    fixtures = [
        "auth_group.json",
        "commissions_commission.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "users_user.json",
        "users_groupinstitutioncommissionuser.json",
    ]

    def test_user_auth_registration(self):
        """
        POST /users/auth/registration/ .

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
