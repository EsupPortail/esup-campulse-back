"""List of tests done on users views with a manager user."""
import json

from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.users.models.user import (
    AssociationUser,
    GroupInstitutionCommissionUser,
    User,
)


class UserViewsManagerTests(TestCase):
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
        """Start a default client used on all tests, retrieves a manager user."""
        cls.unvalidated_user_id = 2
        cls.unvalidated_user_name = "compte-non-valide@mail.tld"
        cls.student_user_id = 11
        cls.student_user_name = "etudiant-asso-site@mail.tld"
        cls.president_user_id = 13
        cls.president_user_name = "president-asso-site@mail.tld"

        cls.manager_misc_user_id = 5
        cls.manager_misc_user_name = "gestionnaire-crous@mail.tld"
        cls.manager_misc_client = Client()
        url_manager_misc = reverse("rest_login")
        data_manager_misc = {
            "username": cls.manager_misc_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.manager_misc_client.post(url_manager_misc, data_manager_misc)

        cls.manager_general_user_id = 3
        cls.manager_general_user_name = "gestionnaire-svu@mail.tld"
        cls.manager_client = Client()
        url_manager = reverse("rest_login")
        data_manager = {
            "username": cls.manager_general_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.manager_client.post(url_manager, data_manager)

    def test_manager_get_associations_user_list(self):
        """
        GET /users/associations/ .

        - A manager user can execute this request.
        - Links between user and associations are returned.
        - Filter by is_validated_by_admin is possible.
        - Filter by institutions is possible.
        """
        associations_user_all_cnt = AssociationUser.objects.count()
        response_all_asso = self.manager_client.get("/users/associations/")
        content_all_asso = json.loads(response_all_asso.content.decode("utf-8"))
        self.assertEqual(response_all_asso.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content_all_asso), associations_user_all_cnt)

        associations_user_validated_cnt = AssociationUser.objects.filter(
            is_validated_by_admin=False
        ).count()
        response_validated_asso = self.manager_client.get(
            "/users/associations/?is_validated_by_admin=false"
        )
        content_validated_asso = json.loads(
            response_validated_asso.content.decode("utf-8")
        )
        self.assertEqual(len(content_validated_asso), associations_user_validated_cnt)

        institutions_ids = [2, 3]
        associations_user_institutions_cnt = AssociationUser.objects.filter(
            association_id__in=Association.objects.filter(
                institution_id__in=institutions_ids
            ).values_list("id", flat=True)
        ).count()
        response_institutions_asso = self.manager_client.get(
            "/users/associations/?institutions=2,3,"
        )
        content_institutions_asso = json.loads(
            response_institutions_asso.content.decode("utf-8")
        )
        self.assertEqual(
            len(content_institutions_asso), associations_user_institutions_cnt
        )

    def test_manager_post_association_user(self):
        """
        POST /users/associations/ .

        - A misc manager user cannot add an association from another institution.
        - A manager user can add an association to a validated student.
        - A manager user can add an association to a non-validated student.
        - A manager cannot be added in an association.
        """
        response_manager_misc = self.manager_misc_client.post(
            "/users/associations/",
            {
                "user": self.student_user_name,
                "association": 1,
            },
        )
        self.assertEqual(response_manager_misc.status_code, status.HTTP_403_FORBIDDEN)

        response_manager = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.student_user_name,
                "association": 1,
            },
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)

        response_manager = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 1,
            },
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)

        response_manager = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.manager_general_user_name,
                "association": 1,
            },
        )
        self.assertEqual(response_manager.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_get_associations_user_detail(self):
        """
        GET /users/{user_id}/associations/ .

        - A manager user can execute this request.
        """
        response_manager = self.manager_client.get(
            f"/users/{self.student_user_id}/associations/"
        )
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        user_associations = AssociationUser.objects.filter(user_id=self.student_user_id)
        user_associations_requested = json.loads(
            response_manager.content.decode("utf-8")
        )
        self.assertEqual(len(user_associations_requested), len(user_associations))

    def test_manager_patch_association_user_update_president(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A manager can execute this request.
        - Link between member and association is correctly updated.
        - If giving president privileges to a member,
              the old president is no longer president of the association.
        - A manager can validate a UserAssociation link.
        - A manager can add a president to an association without one.
        """
        association_id = 2
        asso_user = AssociationUser.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        response = self.manager_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {"is_president": True},
            content_type="application/json",
        )
        asso_user = AssociationUser.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(asso_user.is_president)

        old_president = AssociationUser.objects.get(
            user_id=self.president_user_id, association_id=association_id
        )
        self.assertFalse(old_president.is_president)

        self.assertFalse(len(mail.outbox))
        response = self.manager_client.patch(
            f"/users/{self.unvalidated_user_id}/associations/{association_id}",
            {"is_validated_by_admin": True},
            content_type="application/json",
        )
        asso_user = AssociationUser.objects.get(
            user_id=self.unvalidated_user_id, association_id=association_id
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(asso_user.is_validated_by_admin)
        self.assertTrue(len(mail.outbox))

        association_id = 5
        response = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.student_user_name,
                "association": association_id,
            },
        )
        response = self.manager_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {"is_president": True},
            content_type="application/json",
        )
        asso_user = AssociationUser.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(asso_user.is_president)

    def test_manager_patch_association_user(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A manager can execute this request.
        - Link between member and association is correctly updated.
        """
        asso_user = AssociationUser.objects.get(
            user_id=self.president_user_id, is_president=True
        )
        response = self.manager_client.patch(
            f"/users/{self.president_user_id}/associations/{asso_user.association_id}",
            {"is_president": False},
            content_type="application/json",
        )
        asso_user = AssociationUser.objects.get(user_id=self.president_user_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(asso_user.is_president)

    def test_manager_patch_association_user_unexisting_params(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - Returns a bad request if non-existing user or association in parameters.
        """
        response = self.manager_client.patch(
            "/users/999/associations/999",
            {"is_secretary": True},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_patch_association_user_unexisting_link(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - Returns a bad request if non-existing link between selected user and association.
        """
        response = self.manager_client.patch(
            f"/users/{self.student_user_id}/associations/3",
            {"is_treasurer": True},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_delete_association_user(self):
        """
        DELETE /users/{user_id}/associations/{association_id} .

        - The user must exist.
        - The association must exist.
        - A manager user can execute this request.
        - The link between an association and a user is deleted.
        """
        response = self.manager_client.get(
            f"/users/{self.student_user_id}/associations/"
        )
        first_user_association_id = response.data[0]["id"]

        response_delete = self.manager_client.delete(
            f"/users/99/associations/{str(first_user_association_id)}"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

        response_delete = self.manager_client.delete(
            f"/users/{self.student_user_id}/associations/99"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

        response_delete = self.manager_client.delete(
            f"/users/{self.student_user_id}/associations/{str(first_user_association_id)}"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            AssociationUser.objects.get(
                user_id=self.student_user_id, association_id=first_user_association_id
            )

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

    def test_manager_put_auth_user_detail(self):
        """
        PUT /users/auth/user/ .

        - Request should return an error no matter which role is trying to execute it.
        """
        response_manager = self.manager_client.put(
            "/users/auth/user/", {"username": "Alorsçavag"}
        )
        self.assertEqual(
            response_manager.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_manager_get_user_groups_list(self):
        """
        GET /users/groups/ .

        - A manager user can execute this request.
        - We get the same amount of groups links through the model and through the view.
        """
        response_manager = self.manager_client.get("/users/groups/")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

    def test_manager_post_group_user(self):
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

    def test_manager_get_user_groups_detail(self):
        """
        GET /users/{user_id}/groups/ .

        - A manager user can execute this request.
        """
        response_manager = self.manager_client.get(
            f"/users/{self.student_user_id}/groups/"
        )
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

    def test_manager_delete_user_group(self):
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
