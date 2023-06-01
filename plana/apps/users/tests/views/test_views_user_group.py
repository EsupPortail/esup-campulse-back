from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.users.models.user import AssociationUser, GroupInstitutionFundUser


class AuthUserViewsTests(TestCase):
    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "auth_group_permissions.json",
        "auth_permission.json",
        "commissions_fund.json",
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
        cls.unvalidated_user_name = "compte-non-valide@mail.tld"
        cls.manager_misc_user_name = "gestionnaire-crous@mail.tld"
        cls.user_id_del_group = 2
        cls.user_id_del_group_user_fund = 6
        cls.user_id_del_group_user_insitution = 4
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
        """
        GET /users/groups/ .

        - A student user can execute this request.
        - Only auth user infos are returned.
        """
        response_student = self.student_client.get("/users/groups/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)
        results = GroupInstitutionFundUser.objects.filter(user_id=self.student_user_id)
        self.assertEqual(len(results), len(response_student.data))

    def test_manager_get_user_groups_list(self):
        """
        GET /users/groups/ .

        - A manager user can execute this request.
        - We get the same amount of groups links through the model and through the view.
        """
        response_manager = self.manager_client.get("/users/groups/")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)
        results = GroupInstitutionFundUser.objects.all()
        self.assertEqual(len(results), len(response_manager.data))

    def test_anonymous_get_user_groups_details(self):
        """
        GET /users/{user_id}/groups/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get(
            f"/users/{self.unvalidated_user_id}/groups/"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manager_get_unexisting_association_user(self):
        """
        GET /users/{user_id}/groups/ .

        - 404 error if user not found.
        """
        response_manager = self.manager_client.get("/users/404/groups/")
        self.assertEqual(response_manager.status_code, status.HTTP_404_NOT_FOUND)

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

    def test_anonymous_post_user_groups_404_user(self):
        """
        POST /users/groups/ .

        - A non-existing user cannot be added in a group.
        - username is a mandatory param
        """
        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": 9999, "group": 6},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

        response_anonymous = self.client.post("/users/groups/", {"group": 6})
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_post_user_groups_404_group(self):
        """
        POST /users/groups/ .

        - A user cannot be added in a non-existing group.
        - group is a mandatory param
        """
        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.student_user_name, "group": 9999},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

        response_anonymous = self.client.post(
            "/users/groups/", {"username": self.student_user_name}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_post_user_groups_forbidden(self):
        """
        POST /users/groups/ .

        - An anonymous user cannot add a link between a validated user and a group.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.student_user_name, "group": 4},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_post_user_groups_restricted_group(self):
        """
        POST /users/groups/ .

        - An anonymous user can't add a link with a restricted group to a user.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.unvalidated_user_name, "group": 1},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_post_user_groups_bad_institution(self):
        """
        POST /users/groups/ .

        - institution field must be valid for the given group.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.unvalidated_user_name, "group": 6, "institution": 1},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO : check view
    #    def test_anonymous_post_user_groups_bad_fund(self):
    #        """
    #        POST /users/groups/ .
    #
    #        - fund field must be valid for the given group.
    #        """
    #        response_anonymous = self.anonymous_client.post(
    #            "/users/groups/",
    #            {"username": self.unvalidated_user_name, "group": 6, "fund": 1},
    #        )
    #        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_post_user_groups_success(self):
        """
        POST /users/groups/ .

        - An anonymous user can add a link between a non-validated user and a group.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": self.unvalidated_user_name, "group": 6},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_201_CREATED)

    def test_student_post_user_groups(self):
        """
        POST /users/groups/ .

        - An admin-validated student user cannot execute this request.
        """
        response_student = self.student_client.post(
            "/users/groups/", {"username": self.student_user_name, "group": 6}
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_post_user_groups_other_manager(self):
        """
        POST /users/groups/ .

        - Groups for a general manager can't be changed by another manager.
        """
        response_manager = self.manager_misc_client.post(
            "/users/groups/",
            {"username": self.manager_general_user_name, "group": 4},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_post_user_groups_bad_request(self):
        """
        POST /users/groups/ .

        - A manager group cannot be given to a student.
        - A student group cannot be given to a manager.
        """
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

    def test_manager_post_user_groups_success(self):
        """
        POST /users/groups/ .

        - A manager user can add a group to a validated student.
        - A manager user can add a group to a non-validated student.
        """
        response_manager = self.manager_client.post(
            "/users/groups/",
            {"username": self.student_user_name, "group": 6},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)

        response_manager = self.manager_client.post(
            "/users/groups/",
            {"username": self.unvalidated_user_name, "group": 6},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)

    def test_anonymous_delete_user_group(self):
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.client.delete(
            f"/users/{self.user_id_del_group}/groups/6"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_delete_user_group(self):
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.delete(
            f"/users/{self.user_id_del_group}/groups/6"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_delete_user_group_404(self):
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - Cannot delete group from a non-existing user
        """
        response = self.manager_client.get(f"/users/{self.user_id_del_group}/groups/")
        first_user_group_id = response.data[0]["group"]

        response_delete = self.manager_client.delete(
            f"/users/999/groups/{str(first_user_group_id)}"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_delete_user_group_bad_request(self):
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - Deleting a group to a user still linked to an association is not possible.
        """
        response_delete = self.manager_client.delete("/users/10/groups/5")
        self.assertEqual(response_delete.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_delete_user_group_double_delete(self):
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - A manager user can execute this request.
        - The link between a group and a user is deleted.
        - A link between a group and a use cannot be deleted twice.
        """
        response = self.manager_client.get(f"/users/{self.user_id_del_group}/groups/")
        first_user_group_id = response.data[0]["group"]

        AssociationUser.objects.filter(user_id=self.user_id_del_group).delete()
        first_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group}/groups/{str(first_user_group_id)}"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        first_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group}/groups/{str(first_user_group_id)}"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_delete_user_group_success(self):
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - A manager user can execute this request.
        - The link between a group and a user is deleted.
        - A user should have at least one group.
        """
        response = self.manager_client.get(f"/users/{self.user_id_del_group}/groups/")
        first_user_group_id = response.data[0]["group"]
        second_user_group_id = response.data[1]["group"]

        AssociationUser.objects.filter(user_id=self.user_id_del_group).delete()
        first_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group}/groups/{str(first_user_group_id)}"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        second_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group}/groups/{str(second_user_group_id)}"
        )
        self.assertEqual(
            second_response_delete.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_manager_delete_user_group_fund_404(self):
        """
        DELETE /users/{user_id}/groups/{group_id} .

        - Cannot delete a group from a non-existing user
        """
        response = self.manager_client.get(
            f"/users/{self.user_id_del_group_user_fund}/groups/"
        )
        first_user_group_id = response.data[0]["group"]

        response_delete = self.manager_client.delete(
            f"/users/9999/groups/{str(first_user_group_id)}/funds/1"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_misc_delete_user_group_fund_forbidden(self):
        """
        DELETE /users/{user_id}/groups/{group_id}/funds/{fund_id} .

        - A misc manager user cannot execute this request.
        """
        response = self.manager_client.get(
            f"/users/{self.user_id_del_group_user_fund}/groups/"
        )
        first_user_group_id = response.data[0]["group"]

        response_delete = self.manager_misc_client.delete(
            f"/users/{self.user_id_del_group_user_fund}/groups/{str(first_user_group_id)}/funds/1"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_delete_user_group_fund_double_delete(self):
        """
        DELETE /users/{user_id}/groups/{group_id}/funds/{fund_id} .

        - A manager user can execute this request.
        - The link between a group and a user is deleted.
        - A link between a group and a use cannot be deleted twice.
        """
        response = self.manager_client.get(
            f"/users/{self.user_id_del_group_user_fund}/groups/"
        )
        first_user_group_id = response.data[0]["group"]

        first_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group_user_fund}/groups/{str(first_user_group_id)}/funds/1"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        first_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group_user_fund}/groups/{str(first_user_group_id)}/funds/1"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_delete_user_group_fund_success(self):
        """
        DELETE /users/{user_id}/groups/{group_id}/funds/{fund_id} .

        - A manager user can execute this request.
        - The link between a group and a user is deleted.
        - A user should have at least one group.
        """
        response = self.manager_client.get(
            f"/users/{self.user_id_del_group_user_fund}/groups/"
        )
        first_user_group_id = response.data[0]["group"]
        second_user_group_id = response.data[1]["group"]

        first_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group_user_fund}/groups/{str(first_user_group_id)}/funds/1"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        second_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group_user_fund}/groups/{str(second_user_group_id)}/funds/2"
        )
        self.assertEqual(
            second_response_delete.status_code, status.HTTP_400_BAD_REQUEST
        )

    def test_manager_delete_user_group_institution_404(self):
        """
        DELETE /users/{user_id}/groups/{group_id}/institutions/{institution_id} .

        - Cannot delete a group from a non-existing user
        """
        GroupInstitutionFundUser.objects.create(
            user_id=self.user_id_del_group_user_insitution, group_id=2, institution_id=4
        )
        response = self.manager_client.get(
            f"/users/{self.user_id_del_group_user_insitution}/groups/"
        )
        first_user_group_id = response.data[0]["group"]

        response_delete = self.manager_client.delete(
            f"/users/9999/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_misc_delete_user_group_institution_forbidden(self):
        """
        DELETE /users/{user_id}/groups/{group_id}/institutions/{institution_id} .

        - A misc manager user cannot execute this request.
        """
        GroupInstitutionFundUser.objects.create(
            user_id=self.user_id_del_group_user_insitution, group_id=2, institution_id=4
        )
        response = self.manager_client.get(
            f"/users/{self.user_id_del_group_user_insitution}/groups/"
        )
        first_user_group_id = response.data[0]["group"]

        response_delete = self.manager_misc_client.delete(
            f"/users/{self.user_id_del_group_user_insitution}/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_delete_user_group_institution_double_delete(self):
        """
        DELETE /users/{user_id}/groups/{group_id}/institutions/{institution_id} .

        - A manager user can execute this request.
        - The link between a group and a user is deleted.
        - A link between a group and a use cannot be deleted twice.
        """
        GroupInstitutionFundUser.objects.create(
            user_id=self.user_id_del_group_user_insitution, group_id=2, institution_id=4
        )
        response = self.manager_client.get(
            f"/users/{self.user_id_del_group_user_insitution}/groups/"
        )
        first_user_group_id = response.data[0]["group"]

        first_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group_user_insitution}/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        first_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group_user_insitution}/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_delete_user_group_institution_success(self):
        """
        DELETE /users/{user_id}/groups/{group_id}/institutions/{institution_id} .

        - A genral manager user can execute this request.
        - The link between a group and a user is deleted.
        - A user should have at least one group.
        """
        GroupInstitutionFundUser.objects.create(
            user_id=self.user_id_del_group_user_insitution, group_id=2, institution_id=4
        )
        GroupInstitutionFundUser.objects.filter(
            user_id=self.user_id_del_group_user_insitution, fund_id__isnull=False
        ).delete()
        response = self.manager_client.get(
            f"/users/{self.user_id_del_group_user_insitution}/groups/"
        )
        first_user_group_id = response.data[0]["group"]
        second_user_group_id = response.data[1]["group"]

        first_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group_user_insitution}/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        second_response_delete = self.manager_client.delete(
            f"/users/{self.user_id_del_group_user_insitution}/groups/{str(second_user_group_id)}/institutions/4"
        )
        self.assertEqual(
            second_response_delete.status_code, status.HTTP_400_BAD_REQUEST
        )
