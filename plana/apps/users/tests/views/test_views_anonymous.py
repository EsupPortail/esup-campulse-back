"""
List of tests done on users views with an anonymous user.
"""
from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from django.test import Client, TestCase
from rest_framework import status

from plana.apps.users.models.user import AssociationUsers, User


class UserViewsAnonymousTests(TestCase):
    """
    Main tests class.
    """

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "users_associationusers.json",
        "users_user.json",
        "users_groupinstitutionusers.json",
    ]

    def setUp(self):
        """
        Start a default client used on all tests.
        """
        self.anonymous_client = Client()
        self.unvalidated_user_id = 2
        self.unvalidated_user_name = "compte-non-valide@mail.tld"
        self.student_user_id = 11
        self.student_user_name = "etudiant-asso-site@mail.tld"

    def test_anonymous_get_users_list(self):
        """
        GET /users/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_user(self):
        """
        POST /users/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/",
            {
                "first_name": "Bourvil",
                "last_name": "André",
                "email": "bourvil@splatoon.com",
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_get_user_detail(self):
        """
        GET /users/{id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get(
            f"/users/{self.unvalidated_user_id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_patch_user_detail(self):
        """
        PATCH /users/{id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.patch(
            f"/users/{self.unvalidated_user_id}", {"username": "Bienvenueg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_delete_user_detail(self):
        """
        DELETE /users/{id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.delete(
            f"/users/{self.unvalidated_user_id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_put_user_detail(self):
        """
        PUT /users/{id}
        - Request should return an error no matter which role is trying to execute it.
        """
        response_anonymous = self.anonymous_client.put(
            f"/users/{self.unvalidated_user_id}", {"username": "Aurevoirg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_get_associations_user_list(self):
        """
        GET /users/associations/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/associations/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_association_user(self):
        """
        POST /users/associations/
        - An anonymous user cannot add a link between a validated user and an association.
        - An association cannot have two presidents.
        - An anonymous user can add a link between a non-validated user and an association.
        - A user cannot be added twice in the same association.
        - A non-existing user cannot be added in an association.
        - A user cannot be added in a non-existing association.
        - user field is mandatory.
        - association field is mandatory.
        """

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.student_user_name,
                "association": 2,
                "can_be_president": False,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 3,
                "is_president": True,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 5,
                "can_be_president": False,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_201_CREATED)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 3,
                "can_be_president": False,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": "george-luCAS",
                "association": 2,
                "can_be_president": False,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 99,
                "can_be_president": False,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "association": 3,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_get_associations_user_detail(self):
        """
        GET /users/associations/{user_id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get(
            f"/users/associations/{self.unvalidated_user_id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_patch_association_users(self):
        """
        PATCH /users/associations/{user_id}/{association_id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.patch(
            f"/users/associations/{self.unvalidated_user_id}/2"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_delete_association_user(self):
        """
        DELETE /users/associations/{user_id}/{association_id}
        - An anonymous user cannot execute this request.
        """
        asso_user = AssociationUsers.objects.get(user_id=self.unvalidated_user_id)
        response_anonymous = self.anonymous_client.delete(
            f"/users/associations/{self.unvalidated_user_id}/{asso_user.id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_password_reset(self):
        """
        POST /users/auth/password/reset/
        - An anonymous user can execute this request.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/auth/password/reset/", {"email": self.student_user_name}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)

    def test_anonymous_post_password_reset_confirm(self):
        """
        POST /users/auth/password/reset/confirm/
        - An anonymous user can execute this request.
        """
        user = User.objects.get(id=self.student_user_id)
        response_anonymous = self.anonymous_client.post(
            "/users/auth/password/reset/confirm/",
            {
                "new_password1": "saucisse",
                "new_password2": "saucisse",
                "uid": self.student_user_id,
                "token": default_token_generator.make_token(user),
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)

    def test_anonymous_post_registration_verify_email(self):
        """
        POST /users/auth/registration/verify-email/
        - An anonymous user can execute this request.
        - An anonymous user with association where is_site is false can execute this request.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/auth/registration/",
            {
                "email": "michel.moutarde@jaime-le-raisin-de-table.org",
                "first_name": "Michel",
                "last_name": "Moutarde",
            },
        )
        email_address = EmailAddress.objects.get(
            email="michel.moutarde@jaime-le-raisin-de-table.org"
        )
        key = EmailConfirmationHMAC(email_address=email_address).key
        response_anonymous = self.anonymous_client.post(
            "/users/auth/registration/verify-email/", {"key": key}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)

        response_anonymous = self.anonymous_client.post(
            "/users/auth/registration/",
            {
                "email": "damien.mayonnaise@je-prefere-les-crackers-au-sel.org",
                "first_name": "Damien",
                "last_name": "Mayonnaise",
            },
        )
        user = User.objects.get(
            email="damien.mayonnaise@je-prefere-les-crackers-au-sel.org"
        )
        AssociationUsers.objects.create(user_id=user.id, association_id=3)
        email_address = EmailAddress.objects.get(
            email="damien.mayonnaise@je-prefere-les-crackers-au-sel.org"
        )
        key = EmailConfirmationHMAC(email_address=email_address).key
        response_anonymous = self.anonymous_client.post(
            "/users/auth/registration/verify-email/", {"key": key}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)

    def test_anonymous_get_auth_user_detail(self):
        """
        GET /users/auth/user/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/auth/user/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_patch_auth_user_detail(self):
        """
        PATCH /users/auth/user/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.patch(
            "/users/auth/user/", {"username": "Bienvenueg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_put_auth_user_detail(self):
        """
        PUT /users/auth/user/
        - Request should return an error no matter which role is trying to execute it.
        """
        response_anonymous = self.anonymous_client.put(
            "/users/auth/user/", {"username": "Aurevoirg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_self_consents_user_list(self):
        """
        GET /users/consents/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/consents/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_user_consents(self):
        """
        POST /users/consents/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/consents/", {"user": self.student_user_name, "consent": 1}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_consents_user_list(self):
        """
        GET /users/consents/{user_id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get(
            f"/users/consents/{self.student_user_id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_user_groups_list(self):
        """
        GET /users/groups/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/groups/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_user_groups(self):
        """
        POST /users/groups/
        - An anonymous user cannot add a link between a validated user and a group.
        - An anonymous user can add a link between a non-validated user and a group.
        - A non-existing user cannot be added in a group.
        - A user cannot be added in a non-existing group.
        - username field is mandatory.
        - groups field is mandatory.
        """

        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.student_user_name, "groups": [4, 5]},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.unvalidated_user_name, "groups": [7]},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)

        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": "patricia-CAS", "groups": [6, 7]},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.client.post(
            "/users/groups/", {"username": self.unvalidated_user_name, "groups": [66]}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.client.post("/users/groups/", {"groups": [7]})
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.client.post(
            "/users/groups/", {"username": self.student_user_name}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_get_user_groups_detail(self):
        """
        GET /users/groups/{user_id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get(
            f"/users/groups/{self.unvalidated_user_id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_delete_user_group(self):
        """
        DELETE /users/groups/{user_id}/{group_id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.client.delete(
            f"/users/groups/{self.unvalidated_user_id}/6"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
