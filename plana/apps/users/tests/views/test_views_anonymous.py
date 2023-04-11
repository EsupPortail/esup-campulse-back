"""List of tests done on users views with an anonymous user."""
from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.account.utils import user_pk_to_url_str
from django.conf import settings
from django.core import mail
from django.test import Client, TestCase
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.users.models.user import (
    AssociationUser,
    GroupInstitutionCommissionUser,
    User,
)


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

    def test_anonymous_get_users_list(self):
        """
        GET /users/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_user(self):
        """
        POST /users/ .

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
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_user_detail(self):
        """
        GET /users/{id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get(
            f"/users/{self.unvalidated_user_id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_patch_user_detail(self):
        """
        PATCH /users/{id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.patch(
            f"/users/{self.unvalidated_user_id}", {"username": "Bienvenueg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_delete_user_detail(self):
        """
        DELETE /users/{id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.delete(
            f"/users/{self.unvalidated_user_id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_put_user_detail(self):
        """
        PUT /users/{id} .

        - Request should return an error no matter which role is trying to execute it.
        """
        response_anonymous = self.anonymous_client.put(
            f"/users/{self.unvalidated_user_id}", {"username": "Aurevoirg"}
        )
        self.assertEqual(
            response_anonymous.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_anonymous_get_associations_user_list(self):
        """
        GET /users/associations/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/associations/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_association_user(self):
        """
        POST /users/associations/ .

        - An anonymous user cannot add a link between a validated user and an association.
        - An association cannot have two presidents.
        - An anonymous user cannot validate a link between a user and an association.
        - Link cannot be added to a user without a group where associations can be linked.
        - An anonymous user cannot add a link if association is full.
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
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_403_FORBIDDEN)

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
                "is_validated_by_admin": True,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_403_FORBIDDEN)

        GroupInstitutionCommissionUser.objects.filter(
            user_id=self.unvalidated_user_id, group_id=5
        ).delete()
        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 5,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)
        GroupInstitutionCommissionUser.objects.create(
            user_id=self.unvalidated_user_id, group_id=5
        )

        association = Association.objects.get(id=5)
        old_amount_members_allowed = association.amount_members_allowed
        association.amount_members_allowed = 1
        association.save()
        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 5,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)
        association.amount_members_allowed = old_amount_members_allowed
        association.save()

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 5,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_201_CREATED)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 5,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": "george-luCAS",
                "association": 2,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 99,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "association": 3,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_get_associations_user_detail(self):
        """
        GET /users/{user_id}/associations/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get(
            f"/users/{self.unvalidated_user_id}/associations/"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_patch_association_user(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.patch(
            f"/users/{self.unvalidated_user_id}/associations/2"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_delete_association_user(self):
        """
        DELETE /users/{user_id}/associations/{association_id} .

        - An anonymous user cannot execute this request.
        """
        asso_user = AssociationUser.objects.get(user_id=self.unvalidated_user_id)
        response_anonymous = self.anonymous_client.delete(
            f"/users/{self.unvalidated_user_id}/associations/{asso_user.id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_registration(self):
        """
        POST /users/auth/registration/ .

        - An account with a restricted email can't be created.
        - An account can be created by an anonymous user.
        - An email is received if registration is successful.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/auth/registration/",
            {
                "email": f"gaufre-a-la-menthe@{settings.RESTRICTED_DOMAINS[0]}",
                "first_name": "Gaufre",
                "last_name": "Menthe",
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(len(mail.outbox))

        response_anonymous = self.anonymous_client.post(
            "/users/auth/registration/",
            {
                "email": "gaufre-a-la-menthe@jean-michmail.fr",
                "first_name": "Gaufre",
                "last_name": "Menthe",
                "phone": "36 30",
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(mail.outbox))

    def test_anonymous_post_password_reset(self):
        """
        POST /users/auth/password/reset/ .

        - An anonymous user can execute this request.
        - Nothing happens if email is wrong.
        - An email is received if reset is successful.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/auth/password/reset/", {"email": "auguste-cornouailles@melun.fr"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)
        self.assertFalse(len(mail.outbox))

        response_anonymous = self.anonymous_client.post(
            "/users/auth/password/reset/", {"email": self.student_user_name}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)
        self.assertTrue(len(mail.outbox))

    def test_anonymous_post_password_reset_confirm(self):
        """
        POST /users/auth/password/reset/confirm/ .

        - An anonymous user can execute this request.
        - An email is received if confirmation reset is successful.
        """
        user = User.objects.get(id=self.student_user_id)
        response_anonymous = self.anonymous_client.post(
            "/users/auth/password/reset/confirm/",
            {
                "new_password1": "saucisse",
                "new_password2": "saucisse",
                "uid": user_pk_to_url_str(user),
                "token": default_token_generator.make_token(user),
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)
        self.assertTrue(len(mail.outbox))

    def test_anonymous_post_registration_verify_email(self):
        """
        POST /users/auth/registration/verify-email/ .

        - An anonymous user can execute this request.
        - An email is received if verification is successful.
        - An anonymous user with association where is_site is false can execute this request.
        - An anonymous user with association where is_site is true can execute this request.
        - An anonymous user can verify a new email address associated to an account.
        """
        self.assertFalse(len(mail.outbox))
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
        self.assertTrue(len(mail.outbox))

        email = "damien.mayonnaise@je-prefere-les-crackers-au-sel.org"
        response_anonymous = self.anonymous_client.post(
            "/users/auth/registration/",
            {
                "email": email,
                "first_name": "Damien",
                "last_name": "Mayonnaise",
            },
        )
        user = User.objects.get(email=email)
        AssociationUser.objects.create(user_id=user.id, association_id=3)
        email_address = EmailAddress.objects.get(email=email)
        key = EmailConfirmationHMAC(email_address=email_address).key
        response_anonymous = self.anonymous_client.post(
            "/users/auth/registration/verify-email/", {"key": key}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)

        email_address.verified = False
        email_address.save()
        AssociationUser.objects.create(user_id=user.id, association_id=2)
        key = EmailConfirmationHMAC(email_address=email_address).key
        response_anonymous = self.anonymous_client.post(
            "/users/auth/registration/verify-email/", {"key": key}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)

        new_email = (
            "philippe.bearnaise@meme-si-je-crache-pas-sur-les-chips-au-vinaigre.org"
        )
        user.email = new_email
        user.save()
        new_email_address = EmailAddress.objects.create(
            user_id=user.id, email=new_email
        )
        key = EmailConfirmationHMAC(email_address=new_email_address).key
        response_anonymous = self.anonymous_client.post(
            "/users/auth/registration/verify-email/", {"key": key}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)

    def test_anonymous_get_auth_user_detail(self):
        """
        GET /users/auth/user/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/auth/user/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_patch_auth_user_detail(self):
        """
        PATCH /users/auth/user/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.patch(
            "/users/auth/user/", {"username": "Bienvenueg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_put_auth_user_detail(self):
        """
        PUT /users/auth/user/ .

        - Request should return an error no matter which role is trying to execute it.
        """
        response_anonymous = self.anonymous_client.put(
            "/users/auth/user/", {"username": "Aurevoirg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_delete_auth_user(self):
        """
        DELETE /users/auth/user/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.client.delete("/users/auth/user/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

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
