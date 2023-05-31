import json

from allauth.account.forms import default_token_generator
from allauth.account.models import EmailAddress, EmailConfirmationHMAC
from allauth.account.utils import user_pk_to_url_str
from django.conf import settings
from django.core import mail
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.users.models.user import AssociationUser, User


class AuthUserViewsTests(TestCase):
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
        "users_groupinstitutionfunduser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        url_login = reverse("rest_login")
        # Vars used in unittests
        cls.unvalidated_user_id = 2
        cls.manager_misc_user_name = "gestionnaire-crous@mail.tld"
        cls.president_user_name = "president-asso-site@mail.tld"
        # Start an anonymous client used in some tests
        cls.anonymous_client = Client()

        # Start a student client used in some tests
        cls.student_user_id = 11
        cls.student_user_name = "etudiant-asso-site@mail.tld"
        cls.student_client = Client()
        data_student = {"username": cls.student_user_name, "password": "motdepasse"}
        cls.response_student = cls.student_client.post(url_login, data_student)

        # Start a manager client used in some tests
        cls.manager_general_user_id = 3
        cls.manager_general_user_name = "gestionnaire-svu@mail.tld"
        cls.manager_client = Client()
        data_manager = {
            "username": cls.manager_general_user_name,
            "password": "motdepasse",
        }
        cls.response_manager = cls.manager_client.post(url_login, data_manager)

    def test_anonymous_post_password_change_wrong_passsword(self):
        """
        POST /users/auth/password/change/ .

        - Password must respect some rules.
        """
        fake_passwords = [
            "ah",
            "saucisse",
            "SAUCISSE",
            "Saucisse",
            "Saucisse123",
            "Sociss123+",
        ]
        for fake_password in fake_passwords:
            response_student = self.student_client.post(
                "/users/auth/password/change/",
                {
                    "new_password1": fake_password,
                    "new_password2": fake_password,
                },
            )
            self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_post_password_change(self):
        """
        POST /users/auth/password/change/ .

        - A student user can execute this request.
        - An email is received if confirmation reset is successful.
        """
        response_student = self.student_client.post(
            "/users/auth/password/change/",
            {
                "new_password1": "Saucisse123+",
                "new_password2": "Saucisse123+",
            },
        )
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

    def test_anonymous_post_password_reset_wrong_mail(self):
        """
        POST /users/auth/password/reset/ .

        - An anonymous user can execute this request.
        - Nothing happens if email is wrong.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/auth/password/reset/", {"email": "auguste-cornouailles@melun.fr"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)
        self.assertFalse(len(mail.outbox))

    def test_anonymous_post_password_reset_success(self):
        """
        POST /users/auth/password/reset/ .

        - An anonymous user can execute this request.
        - An email is received if reset is successful.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/auth/password/reset/", {"email": self.student_user_name}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)
        self.assertTrue(len(mail.outbox))

    def test_anonymous_post_password_reset_confirm_wrong_passsword(self):
        """
        POST /users/auth/password/reset/confirm/ .

        - Password must respect some rules.
        """
        fake_passwords = [
            "ah",
            "saucisse",
            "SAUCISSE",
            "Saucisse",
            "Saucisse123",
            "Sociss123+",
        ]
        user = User.objects.get(id=self.student_user_id)
        for fake_password in fake_passwords:
            response_anonymous = self.anonymous_client.post(
                "/users/auth/password/reset/confirm/",
                {
                    "new_password1": fake_password,
                    "new_password2": fake_password,
                    "uid": user_pk_to_url_str(user),
                    "token": default_token_generator.make_token(user),
                },
            )
            self.assertEqual(
                response_anonymous.status_code, status.HTTP_400_BAD_REQUEST
            )

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
                "new_password1": "Saucisse123+",
                "new_password2": "Saucisse123+",
                "uid": user_pk_to_url_str(user),
                "token": default_token_generator.make_token(user),
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)
        self.assertTrue(len(mail.outbox))

    def test_anonymous_post_registration_bad_request(self):
        """
        POST /users/auth/registration/ .

        - An account with a restricted email can't be created.
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

    def test_anonymous_post_registration_success(self):
        """
        POST /users/auth/registration/ .

        - An account can be created by an anonymous user.
        - An email is received if registration is successful.
        """
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

    def test_anonymous_post_double_registration(self):
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

        response = self.anonymous_client.post("/users/auth/registration/", user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.anonymous_client.post("/users/auth/registration/", user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

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

    def test_manager_get_auth_user_detail(self):
        """
        GET /users/auth/user/ .

        - A manager user can execute this request.
        - A manager user gets correct data when executing the request.
        """
        response_manager = self.manager_client.get("/users/auth/user/")
        user = User.objects.get(username=self.manager_general_user_name)
        user_data = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)
        self.assertEqual(user_data["username"], user.username)

    def test_put_auth_user_detail(self):
        """
        PUT /users/auth/user/ .

        - Always returns a 405 no matter which role tries to access it.
        """
        response_manager = self.manager_client.put(
            "/users/auth/user/", {"username": "Coucouw"}
        )
        self.assertEqual(
            response_manager.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_anonymous_patch_auth_user_detail(self):
        """
        PATCH /users/auth/user/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.patch(
            "/users/auth/user/", {"username": "Bienvenueg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_patch_auth_user_detail_restricted_fields(self):
        """
        PATCH /users/auth/user/ .

        - A student user cannot update his validation status.
        - A student user cannot update his username.
        - A student user cannot update his permission to submit projects.
        """
        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"is_validated_by_admin": False},
            content_type="application/json",
        )
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)
        student_user = User.objects.get(username=self.student_user_name)
        self.assertTrue(student_user.is_validated_by_admin)

        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"username": "jesuisunusurpateur"},
            content_type="application/json",
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"can_submit_projects": False},
            content_type="application/json",
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_patch_auth_user_detail_mail_already_used(self):
        """
        PATCH /users/auth/user/ .

        - A student user cannot update his email address with an address from another account.
        """
        new_email = self.president_user_name
        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"email": new_email},
            content_type="application/json",
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_patch_auth_user_detail_restricted_mail(self):
        """
        PATCH /users/auth/user/ .

        - A student user cannot update his email address with domain-restricted email address.
        """
        new_email = f"mon-esprit-est-mortadelle@{settings.RESTRICTED_DOMAINS[0]}"
        response_student = self.student_client.patch(
            "/users/auth/user/",
            data={"email": new_email},
            content_type="application/json",
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_patch_auth_user_detail_success(self):
        """
        PATCH /users/auth/user/ .

        - A student user can execute this request.
        - A student user can update his email address.
        - Updating the email address doesn't change the username without validation.
        """
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

    def test_anonymous_delete_auth_user(self):
        """
        DELETE /users/auth/user/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.client.delete("/users/auth/user/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_delete_auth_user(self):
        """
        DELETE /users/auth/user/ .

        - A user should be able to delete his own account.
        """
        response_student = self.student_client.delete("/users/auth/user/")
        student_user_query = User.objects.filter(username=self.student_user_name)
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)
        self.assertEqual(len(student_user_query), 0)
