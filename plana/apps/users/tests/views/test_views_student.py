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
