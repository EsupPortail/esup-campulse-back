"""List of tests done on users views with a student user."""
import datetime
import json

from django.conf import settings
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

# from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import AssociationUsers, User


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
        "consents_gdprconsent.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "users_associationusers.json",
        "users_gdprconsentusers.json",
        "users_user.json",
        "users_groupinstitutioncommissionusers.json",
    ]

    def setUp(self):
        """Clients used on all tests (simple student user, president of an association)."""
        self.unvalidated_user_id = 2
        self.unvalidated_user_name = "compte-non-valide@mail.tld"

        self.student_user_id = 11
        self.student_user_name = "etudiant-asso-site@mail.tld"
        self.student_client = Client()
        url = reverse("rest_login")
        data = {
            "username": self.student_user_name,
            "password": "motdepasse",
        }
        self.response_student = self.student_client.post(url, data)

        self.president_user_id = 13
        self.president_user_name = "president-asso-site@mail.tld"
        self.president_student_client = Client()
        url = reverse("rest_login")
        data = {
            "username": self.president_user_name,
            "password": "motdepasse",
        }
        self.response_president = self.president_student_client.post(url, data)

    def test_student_get_users_list(self):
        """
        GET /users/ .

        - A student user get users in the same associations with partial data.
        """
        response_student = self.student_client.get("/users/")
        users = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)
        self.assertIsNotNone(users[0]["firstName"])
        with self.assertRaises(KeyError):
            print(users[0]["email"])

    def test_student_post_user(self):
        """
        POST /users/ .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.post(
            "/users/",
            {
                "first_name": "Bourvil",
                "last_name": "André",
                "email": "bourvil@splatoon.com",
            },
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_user_detail(self):
        """
        GET /users/{id} .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.get(f"/users/{self.student_user_id}")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_patch_user_detail(self):
        """
        PATCH /users/{id} .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.patch(
            f"/users/{self.unvalidated_user_id}",
            data={"username": "Bienvenueg"},
            content_type="application/json",
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_delete_user_detail(self):
        """
        DELETE /users/{id} .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.delete(
            f"/users/{self.unvalidated_user_id}"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_put_user_detail(self):
        """
        PUT /users/{id} .

        - Request should return an error no matter which role is trying to execute it.
        """
        response_student = self.student_client.put(
            f"/users/{self.unvalidated_user_id}", {"username": "Aurevoirg"}
        )
        self.assertEqual(response_student.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_get_associations_user_list(self):
        """
        GET /users/associations/ .

        - A student user can execute this request.
        - A student user gets correct association user list data.
        """
        response_student = self.student_client.get("/users/associations/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        associations_user_cnt = AssociationUsers.objects.filter(
            user_id=self.student_user_id
        ).count()
        content = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(len(content), associations_user_cnt)

        response_president = self.president_student_client.get(
            "/users/associations/?association_id=2"
        )
        associations_user_cnt = AssociationUsers.objects.filter(
            association_id=2
        ).count()
        content = json.loads(response_president.content.decode("utf-8"))
        self.assertEqual(len(content), associations_user_cnt)

    def test_student_post_association_user(self):
        """
        POST /users/associations/ .

        - An admin-validated student user can execute this request.
        - An admin-validated student cannot validate its own link.
        """
        response_student = self.student_client.post(
            "/users/associations/",
            {
                "user": self.student_user_name,
                "association": 5,
                "can_be_president": False,
            },
        )
        self.assertEqual(response_student.status_code, status.HTTP_201_CREATED)
        user_asso = AssociationUsers.objects.get(
            user_id=self.student_user_id, association_id=5
        )
        self.assertFalse(user_asso.is_validated_by_admin)

    def test_student_get_associations_user_detail(self):
        """
        GET /users/{user_id}/associations/ .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.get(
            f"/users/{self.unvalidated_user_id}/associations/"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_patch_association_users(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A simple student user cannot execute this request.
        """
        asso_user = AssociationUsers.objects.get(user_id=self.student_user_id)
        response_student = self.student_client.patch(
            f"/users/{self.student_user_id}/associations/{asso_user.association_id}"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_patch_association_users_president_remove_president(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A student president cannot remove his own privileges.
        """
        asso_user = AssociationUsers.objects.get(
            user_id=self.president_user_id, is_president=True
        )
        response_president = self.president_student_client.patch(
            f"/users/{self.president_user_id}/associations/{asso_user.association_id}",
            {"is_president": False},
            content_type="application/json",
        )
        self.assertEqual(response_president.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_patch_association_users_validation(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A student president of an association cannot change the validation status.
        """
        association_id = 2
        AssociationUsers.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {"is_validated_by_admin": False},
            content_type="application/json",
        )
        AssociationUsers.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        self.assertEqual(response_president.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_patch_association_users_president(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A student president of an association cannot update president status.
        - A student president of an association can execute this request.
        - A can_be_president of an association cannot PATCH can_be_president.
        - A student president of an association can update vice-president, secretary and treasurer.
        - can_be_president_from cannot comes after can_be_president_to
        """
        association_id = 2
        asso_user = AssociationUsers.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {
                "can_be_president": True,
                "is_president": True,
                "is_secretary": False,
                "is_treasurer": False,
            },
            content_type="application/json",
        )
        asso_user = AssociationUsers.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        self.assertEqual(response_president.status_code, status.HTTP_400_BAD_REQUEST)

        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {
                "can_be_president": True,
                "can_be_president_from": "2023-03-22",
                "can_be_president_to": "2023-03-29",
                "is_secretary": True,
                "is_treasurer": False,
            },
            content_type="application/json",
        )
        asso_user = AssociationUsers.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        self.assertEqual(response_president.status_code, status.HTTP_200_OK)
        self.assertEqual(asso_user.can_be_president_from, datetime.date(2023, 3, 22))
        self.assertTrue(asso_user.can_be_president)
        self.assertFalse(asso_user.is_president)
        self.assertTrue(asso_user.is_secretary)
        self.assertFalse(asso_user.is_treasurer)
        self.assertFalse(asso_user.is_vice_president)

        response_student = self.student_client.patch(
            f"/users/{self.unvalidated_user_id}/associations/{association_id}",
            {
                "can_be_president": True,
            },
            content_type="application/json",
        )
        asso_user = AssociationUsers.objects.get(
            user_id=self.unvalidated_user_id, association_id=association_id
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(asso_user.can_be_president)

        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {
                "can_be_president_to": None,
                "is_treasurer": True,
            },
            content_type="application/json",
        )
        asso_user = AssociationUsers.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        self.assertEqual(response_president.status_code, status.HTTP_200_OK)
        self.assertEqual(asso_user.can_be_president_to, None)
        self.assertFalse(asso_user.is_president)
        self.assertFalse(asso_user.is_secretary)
        self.assertTrue(asso_user.is_treasurer)
        self.assertFalse(asso_user.is_vice_president)

        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {
                "can_be_president_from": None,
                "is_vice_president": True,
            },
            content_type="application/json",
        )
        asso_user = AssociationUsers.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        self.assertEqual(response_president.status_code, status.HTTP_200_OK)
        self.assertFalse(asso_user.is_president)
        self.assertFalse(asso_user.is_secretary)
        self.assertFalse(asso_user.is_treasurer)
        self.assertTrue(asso_user.is_vice_president)

        """
        old_president = AssociationUsers.objects.get(
            user_id=self.president_user_id, association_id=association_id
        )
        self.assertTrue(old_president.can_be_president)
        self.assertFalse(old_president.is_president)
        """

        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {
                "can_be_president_from": "2023-03-22",
                "can_be_president_to": "2023-03-15",
            },
            content_type="application/json",
        )
        self.assertEqual(response_president.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_patch_association_users_other_president(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A student president of another association cannot execute this request.
        """
        response_president = self.president_student_client.patch(
            f"/users/{self.president_user_id}/associations/3",
            {"is_secretary": True},
            content_type="application/json",
        )
        self.assertEqual(response_president.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_delete_user_association(self):
        """
        DELETE /users/{user_id}/associations/{association_id} .

        - A student user cannot execute this request.
        """
        asso_user = AssociationUsers.objects.get(user_id=self.unvalidated_user_id)
        response_student = self.student_client.delete(
            f"/users/{self.unvalidated_user_id}/associations/{asso_user.id}"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_get_association_users(self):
        """
        GET /users/{user_id}/associations/{association_id} .

        - Request should return an error no matter which role is trying to execute it.
        """
        response_student = self.student_client.get("/users/999/associations/999")
        self.assertEqual(response_student.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_put_association_users(self):
        """
        PUT /users/{user_id}/associations/{association_id} .

        - Request should return an error no matter which role is trying to execute it.
        """
        response_student = self.student_client.put(
            "/users/999/associations/999", {"is_treasurer": True}
        )
        self.assertEqual(response_student.status_code, status.HTTP_404_NOT_FOUND)

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
        self.assertEqual(response_student.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_delete_auth_user(self):
        """
        DELETE /users/auth/user/ .

        - A user should be able to delete his own account.
        """
        response_student = self.student_client.delete("/users/auth/user/")
        student_user_query = User.objects.filter(username=self.student_user_name)
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)
        self.assertEqual(len(student_user_query), 0)

    def test_student_get_consents_user_list(self):
        """
        GET /users/consents/ .

        - A student user can execute this request.
        - A student user gets only his own consents.
        """
        """
        consents_user_cnt = GDPRConsentUsers.objects.filter(
            user_id=self.student_user_id
        ).count()
        response_student = self.student_client.get("/users/consents/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        content = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(len(content), consents_user_cnt)
        """

    def test_student_post_user_consents(self):
        """
        POST /users/consents/ .

        - A student user can execute this request.
        - A student user cannot give the same consent twice.
        - A non-existing user cannot have a consent.
        - A student user cannot give an unexisting consent.
        - user field is mandatory.
        - consent field is mandatory.
        """
        """
        response_student = self.student_client.post(
            "/users/consents/", {"user": self.student_user_name, "consent": 1}
        )
        self.assertEqual(response_student.status_code, status.HTTP_201_CREATED)

        response_student = self.student_client.post(
            "/users/consents/", {"user": self.student_user_name, "consent": 1}
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

        response_student = self.student_client.post(
            "/users/consents/", {"user": "brice-de-nice-CASsé", "consent": 1}
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

        response_student = self.student_client.post(
            "/users/consents/", {"user": self.student_user_name, "consent": 75}
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

        response_student = self.student_client.post("/users/consents/", {"consent": 75})
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

        response_student = self.student_client.post(
            "/users/consents/", {"user": self.student_user_name}
        )
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)
        """

    def test_student_get_consents_user_detail(self):
        """
        GET /users/consents/{user_id} .

        - A student user cannot execute this request.
        """
        """
        response_student = self.student_client.get(
            f"/users/consents/{self.student_user_id}"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)
        """

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
        self.assertEqual(response_student.status_code, status.HTTP_400_BAD_REQUEST)

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
        "users_groupinstitutioncommissionusers.json",
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
