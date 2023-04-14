from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.users.models import AssociationUser, GroupInstitutionCommissionUser


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
        "users_groupinstitutioncommissionuser.json",
        "users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        url_login = reverse("rest_login")
        # Vars used in unittests
        cls.unvalidated_user_id = 2
        cls.unvalidated_user_name = "compte-non-valide@mail.tld"
        cls.manager_misc_user_name = "gestionnaire-crous@mail.tld"
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

        # Start a manager misc client used in some tests
        cls.manager_misc_user_id = 5
        cls.manager_misc_user_name = "gestionnaire-crous@mail.tld"
        cls.manager_misc_client = Client()
        data_manager_misc = {
            "username": cls.manager_misc_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.manager_misc_client.post(url_login, data_manager_misc)

    def test_anonymous_get_user_groups_list(self):
        """
        GET /users/groups/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/groups/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_get_user_groups_list(self):
        # TODO : check return of the request ?
        """
        GET /users/groups/ .

        - A student user can execute this request.
        """
        response_student = self.student_client.get("/users/groups/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

    def test_manager_get_user_groups_list(self):
        """
        GET /users/groups/ .

        - A manager user can execute this request.
        - We get the same amount of groups links through the model and through the view.
        """
        response_manager = self.manager_client.get("/users/groups/")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

    def test_anonymous_get_user_groups_details(self):
        """
        GET /users/{user_id}/groups/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get(
            f"/users/{self.unvalidated_user_id}/groups/"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_get_user_groups_details(self):
        """
        GET /users/{user_id}/groups/ .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.get(
            f"/users/{self.student_user_id}/groups/"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_get_user_groups_details(self):
        """
        GET /users/{user_id}/groups/ .

        - A manager user can execute this request.
        """
        response_manager = self.manager_client.get(
            f"/users/{self.student_user_id}/groups/"
        )
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

    def test_anonymous_post_user_groups(self):
        # TODO : split test
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

    def test_student_post_user_groups(self):
        """
        POST /users/groups/ .

        - An admin-validated student user cannot execute this request.
        """
        response_student = self.student_client.post(
            "/users/groups/", {"username": self.student_user_name, "group": 6}
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_post_user_groups(self):
        # TODO : split test
        """
        POST /users/groups/ .

        - A manager user can add a group to a validated student.
        - A manager user can add a group to a non-validated student.
        - Groups for a general manager can't be changed by another manager.
        - A manager group cannot be given to a student.
        - A student group cannot be given to a manager.
        """
        response_manager = self.manager_client.post(
            "/users/groups/",
            {"username": self.student_user_name, "group": 6},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        response_manager = self.manager_client.post(
            "/users/groups/",
            {"username": self.unvalidated_user_name, "group": 6},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        response_manager = self.manager_misc_client.post(
            "/users/groups/",
            {"username": self.manager_general_user_name, "group": 4},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_400_BAD_REQUEST)

        response_manager = self.manager_client.post(
            "/users/groups/",
            {"username": self.student_user_name, "group": 2, "institution": 1},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_400_BAD_REQUEST)

        response_manager = self.manager_client.post(
            "/users/groups/",
            {"username": self.manager_misc_user_name, "group": 6},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_delete_user_group(self):
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.client.delete(
            f"/users/{self.unvalidated_user_id}/groups/6"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_delete_user_group(self):
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.delete(
            f"/users/{self.student_user_id}/groups/6"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_delete_user_group(self):
        # TODO : split test
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - The user must exist.
        - Deleting a group still linked to an association is not possible.
        - A manager user can execute this request.
        - The link between a group and a user is deleted.
        - A user should have at least one group.
        """
        user_id = 2
        response = self.manager_client.get(f"/users/{user_id}/groups/")
        first_user_group_id = response.data[0]["group"]
        second_user_group_id = response.data[1]["group"]

        response_delete = self.manager_client.delete(
            f"/users/99/groups/{str(first_user_group_id)}"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

        response_delete = self.manager_client.delete("/users/10/groups/5")
        self.assertEqual(response_delete.status_code, status.HTTP_400_BAD_REQUEST)

        AssociationUser.objects.filter(user_id=user_id).delete()
        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_404_NOT_FOUND)

        second_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(second_user_group_id)}"
        )
        self.assertEqual(
            second_response_delete.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_manager_delete_user_group_commission(self):
        # TODO : split test
        """
        DELETE /users/{user_id}/groups/{group_id}/commissions/{commission_id} .

        - The user must exist.
        - A misc manager user cannot execute this request.
        - A manager user can execute this request.
        - The link between a group and a user is deleted.
        - A user should have at least one group.
        """
        user_id = 6
        response = self.manager_client.get(f"/users/{user_id}/groups/")
        first_user_group_id = response.data[0]["group"]
        second_user_group_id = response.data[1]["group"]

        response_delete = self.manager_client.delete(
            f"/users/99/groups/{str(first_user_group_id)}/commissions/1"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

        response_delete = self.manager_misc_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/commissions/1"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN)

        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/commissions/1"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/commissions/1"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_404_NOT_FOUND)

        second_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(second_user_group_id)}/commissions/2"
        )
        self.assertEqual(
            second_response_delete.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_manager_delete_user_group_institution(self):
        # TODO : split test
        """
        DELETE /users/{user_id}/groups/{group_id}/institutions/{institution_id} .

        - The user must exist.
        - A misc manager user cannot execute this request.
        - A genral manager user can execute this request.
        - The link between a group and a user is deleted.
        - A user should have at least one group.
        """
        user_id = 4
        GroupInstitutionCommissionUser.objects.create(
            user_id=user_id, group_id=2, institution_id=4
        )
        GroupInstitutionCommissionUser.objects.filter(
            user_id=user_id, commission_id__isnull=False
        ).delete()
        response = self.manager_client.get(f"/users/{user_id}/groups/")
        first_user_group_id = response.data[0]["group"]
        second_user_group_id = response.data[1]["group"]

        response_delete = self.manager_client.delete(
            f"/users/99/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

        response_delete = self.manager_misc_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN)

        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_404_NOT_FOUND)

        second_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(second_user_group_id)}/institutions/4"
        )
        self.assertEqual(
            second_response_delete.status_code, status.HTTP_400_BAD_REQUEST
        )
