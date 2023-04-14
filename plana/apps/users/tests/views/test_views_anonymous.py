"""List of tests done on users views with an anonymous user."""
from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.account.utils import user_pk_to_url_str
from django.conf import settings
from django.core import mail
from django.test import Client, TestCase
from rest_framework import status

from plana.apps.users.models.user import AssociationUser, User


class UserViewsAnonymousTests(TestCase):
    """Main tests class."""

    fixtures = [
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

    def setUp(self):
        """Start a default client used on all tests."""
        self.anonymous_client = Client()
        self.unvalidated_user_id = 2
        self.unvalidated_user_name = "compte-non-valide@mail.tld"
        self.student_user_id = 11
        self.student_user_name = "etudiant-asso-site@mail.tld"
        self.manager_general_user_id = 3
        self.manager_general_user_name = "gestionnaire-svu@mail.tld"

    def test_anonymous_get_user_groups_list(self):
        """
        GET /users/groups/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/groups/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_user_groups(self):
        """
        POST /users/groups/ .

        - An anonymous user cannot add a link between a validated user and a group.
        - An anonymous user can't add a link with a restricted group to a user.
        - institution field must be valid for the given group.
        - commission field must be valid for the given group.
        - An anonymous user can add a link between a non-validated user and a group.
        - A non-existing user cannot be added in a group.
        - A user cannot be added in a non-existing group.
        - username field is mandatory.
        - group field is mandatory.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.student_user_name, "group": 4},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_403_FORBIDDEN)

        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.unvalidated_user_name, "group": 1},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.unvalidated_user_name, "group": 6, "institution": 1},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.unvalidated_user_name, "group": 6, "commission": 1},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.unvalidated_user_name, "group": 6},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)

        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": 99, "group": 6},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

        response_anonymous = self.client.post(
            "/users/groups/", {"username": self.unvalidated_user_name, "group": 66}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

        response_anonymous = self.client.post("/users/groups/", {"group": 6})
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

        response_anonymous = self.client.post(
            "/users/groups/", {"username": self.student_user_name}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_get_user_groups_detail(self):
        """
        GET /users/{user_id}/groups/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get(
            f"/users/{self.unvalidated_user_id}/groups/"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_delete_user_group(self):
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.client.delete(
            f"/users/{self.unvalidated_user_id}/groups/6"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
