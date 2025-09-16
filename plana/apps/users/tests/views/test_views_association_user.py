"""List of tests done on association_user views."""

import datetime
import json

from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.history.models.history import History
from plana.apps.users.models.user import AssociationUser


class AssociationUserViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "tests/account_emailaddress.json",
        "associations_activityfield.json",
        "tests/associations_association.json",
        "auth_group.json",
        "auth_permission.json",
        "tests/commissions_fund.json",
        "tests/institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "tests/users_associationuser.json",
        "tests/users_groupinstitutionfunduser.json",
        "tests/users_user.json",
    ]

    @classmethod
    def setUpTestData(cls):
        url_login = reverse("rest_login")
        # Vars used in unittests
        cls.unvalidated_user_id = 2
        cls.unvalidated_user_name = "compte-non-valide@mail.tld"
        cls.misc_user_id = 9
        cls.user_in_asso_id = 10

        # Start a student client used in some tests
        cls.student_user_id = 11
        cls.student_user_name = "etudiant-asso-site@mail.tld"
        cls.student_asso_id = 2
        cls.student_client = Client()
        data_student = {"username": cls.student_user_name, "password": "motdepasse"}
        cls.response_student = cls.student_client.post(url_login, data_student)

        # Start a student president of an association client used in some tests
        cls.president_user_id = 13
        cls.president_user_name = "president-asso-site@mail.tld"
        cls.president_student_client = Client()
        data_president = {
            "username": cls.president_user_name,
            "password": "motdepasse",
        }
        cls.response_president = cls.president_student_client.post(url_login, data_president)

        # Start a manager client used in some tests
        cls.manager_general_user_id = 3
        cls.manager_general_user_name = "gestionnaire-svu@mail.tld"
        cls.manager_client = Client()
        data_manager = {
            "username": cls.manager_general_user_name,
            "password": "motdepasse",
        }
        cls.response_manager = cls.manager_client.post(url_login, data_manager)

        # Start a manager institution client used in some tests
        cls.manager_inst_user_id = 4
        cls.manager_inst_institution_id = 3
        cls.managed_inst_user_id = 14
        cls.manager_inst_user_name = "gestionnaire-uha@mail.tld"
        cls.manager_inst_client = Client()
        data_manager_inst = {
            "username": cls.manager_inst_user_name,
            "password": "motdepasse",
        }
        cls.response_manager_inst = cls.manager_inst_client.post(url_login, data_manager_inst)

        # Start a manager misc client used in some tests
        cls.manager_misc_user_id = 5
        cls.manager_misc_user_name = "gestionnaire-crous@mail.tld"
        cls.manager_misc_client = Client()
        data_manager_misc = {
            "username": cls.manager_misc_user_name,
            "password": "motdepasse",
        }
        cls.response = cls.manager_misc_client.post(url_login, data_manager_misc)

    def test_student_get_association_user_list_global(self):
        """
        GET /users/associations/ .

        - A student user always retrieves an empty list.
        """
        response_all_asso = self.student_client.get("/users/associations/")
        content_all_asso = json.loads(response_all_asso.content.decode("utf-8"))
        self.assertEqual(response_all_asso.status_code, status.HTTP_200_OK)
        self.assertEqual(content_all_asso, [])

    def test_manager_get_association_user_list_global(self):
        """
        GET /users/associations/ .

        - A manager user can execute this request.
        - Links between user and associations are returned.
        - Links between user and associations are filtered by authorized institution.
        """
        associations_user_all_cnt = AssociationUser.objects.filter(user__is_validated_by_admin=True).count()
        response_all_asso = self.manager_client.get("/users/associations/")
        content_all_asso = json.loads(response_all_asso.content.decode("utf-8"))
        self.assertEqual(response_all_asso.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content_all_asso), associations_user_all_cnt)

        associations_user_inst_cnt = AssociationUser.objects.filter(
            user__is_validated_by_admin=True,
            association__institution=self.manager_inst_institution_id
        ).count()
        response_all_asso = self.manager_inst_client.get("/users/associations/")
        content_asso_inst = json.loads(response_all_asso.content.decode("utf-8"))
        self.assertEqual(len(content_asso_inst), associations_user_inst_cnt)

    def test_manager_get_association_user_list_search(self):
        """
        GET /users/associations/ .

        - A manager user can execute this request.
        - Filter by is_validated_by_admin is possible.
        """
        associations_user_validated_cnt = AssociationUser.objects.filter(
            user__is_validated_by_admin=True,
            is_validated_by_admin=False
        ).count()
        response_validated_asso = self.manager_client.get("/users/associations/?is_validated_by_admin=false")
        content_validated_asso = json.loads(response_validated_asso.content.decode("utf-8"))
        self.assertEqual(len(content_validated_asso), associations_user_validated_cnt)

    def test_manager_get_unexisting_association_user(self):
        """
        GET /users/{user_id}/associations/ .

        - 404 error if user not found.
        """
        response_manager = self.manager_client.get("/users/404/associations/")
        self.assertEqual(response_manager.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_get_association_user_detail(self):
        """
        GET /users/{user_id}/associations/ .

        - A student user can execute this request only if given user is the auth user.
        - All of its AssociationUser links are returned.
        """
        response_student = self.student_client.get(f"/users/1/associations/")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

        asso_user_student_count = AssociationUser.objects.filter(user_id=self.student_user_id).count()
        response_student = self.student_client.get(f"/users/{self.student_user_id}/associations/")
        data_response_student = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data_response_student), asso_user_student_count)

    def test_manager_get_association_user_detail(self):
        """
        GET /users/{user_id}/associations/ .

        - A manager user can execute this request.
        - Correct data is returned.
        """
        response_manager = self.manager_client.get(f"/users/{self.student_user_id}/associations/")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        user_associations = AssociationUser.objects.filter(user_id=self.student_user_id)
        user_associations_requested = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(len(user_associations_requested), len(user_associations))

    def test_post_association_user_forbidden(self):
        """
        POST /users/associations/ .

        - A manager not linked to given association's institution cannot execute this request.
        - A basic user cannot execute this request on another user.
        """
        # TODO : uncomment when is_staff permissions are better defined
        #response_manager = self.manager_inst_client.post(
        #    "/users/associations/",
        #    {
        #            "user": self.student_user_id,
        #            "association": Association.objects.exclude(institution=self.manager_inst_institution_id).first().pk
        #    }
        #)
        #self.assertEqual(response_manager.status_code, status.HTTP_403_FORBIDDEN)
        response_student = self.student_client.post(
            "/users/associations/",
            {
                    "user": self.unvalidated_user_id,
                    "association": Association.objects.first().pk
            }
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_post_association_user_missing_group(self):
        """
        POST /users/associations/ .

        - Cannot execute this request if given user is not a member of a group that can have association.
        """
        response = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.misc_user_id,
                "association": Association.objects.first().pk
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("missing_group", response.data)

    def test_post_association_user_too_many_members(self):
        """
        POST /users/associations/ .

        - Cannot execute this request if association is full.
        """
        asso_id = 1
        asso_users = [
            AssociationUser(user_id=1, association_id=asso_id),
            AssociationUser(user_id=2, association_id=asso_id),
            AssociationUser(user_id=3, association_id=asso_id),
            AssociationUser(user_id=4, association_id=asso_id),
        ]
        AssociationUser.objects.bulk_create(asso_users)

        response = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.student_user_id,
                "association": asso_id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("too_many_members", response.data)

    def test_post_association_user_president(self):
        """
        POST /users/associations/ .

        - Cannot execute this request with given user set as president if association already have one.
        """
        response = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.user_in_asso_id,
                "association": self.student_asso_id,
                "is_president": True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("president", response.data)

    def test_post_association_user_already_exists(self):
        """
        POST /users/associations/ .

        - Cannot execute this request if given user is already linked to given association.
        """
        response = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.student_user_id,
                "association": self.student_asso_id
            }
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("non_field_errors", response.data)

    def test_post_association_user_ok_user(self):
        """
        POST /users/associations/ .

        - A student user can execute this request.
        - An email is sent to dedicated managers.
        - Attribute "is_validated_by_admin" is set to False by default.
        """
        response = self.student_client.post(
            "/users/associations/",
            {
                "user": self.student_user_id,
                "association": 1,
                "is_validated_by_admin": True
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(mail.outbox))
        self.assertFalse(response.data["is_validated_by_admin"])

    def test_post_association_user_ok_manager(self):
        """
        POST /users/associations/ .

        - A manager user can execute this request.
        - No email is sent to dedicated managers.
        - Attribute "is_validated_by_admin" is set to True by default.
        """
        response = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.student_user_id,
                "association": 1
            }
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertFalse(len(mail.outbox))
        self.assertTrue(response.data["is_validated_by_admin"])

    def test_student_patch_association_user(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A simple student user cannot execute this request.
        """
        asso_user = AssociationUser.objects.get(user_id=self.student_user_id)
        response_student = self.student_client.patch(
            f"/users/{self.student_user_id}/associations/{asso_user.association_id}"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_patch_association_user_president_remove_president(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A student president cannot remove his own privileges.
        """
        asso_user = AssociationUser.objects.get(user_id=self.president_user_id, is_president=True)
        response_president = self.president_student_client.patch(
            f"/users/{self.president_user_id}/associations/{asso_user.association_id}",
            {"is_president": False},
            content_type="application/json",
        )
        self.assertEqual(response_president.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_patch_association_user_validation(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A student president of an association cannot change the validation status.
        """
        association_id = 2
        AssociationUser.objects.get(user_id=self.student_user_id, association_id=association_id)
        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {"is_validated_by_admin": False},
            content_type="application/json",
        )
        AssociationUser.objects.get(user_id=self.student_user_id, association_id=association_id)
        self.assertEqual(response_president.status_code, status.HTTP_403_FORBIDDEN)

    def test_student_patch_association_user_president_forbidden(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A student president of an association cannot update president status.
        """
        association_id = 2
        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {
                "is_president": True,
                "is_secretary": False,
                "is_treasurer": False,
            },
            content_type="application/json",
        )
        asso_user = AssociationUser.objects.get(user_id=self.student_user_id, association_id=association_id)
        self.assertEqual(response_president.status_code, status.HTTP_403_FORBIDDEN)
        self.assertFalse(asso_user.is_president)

    def test_student_patch_association_user_president_bad_request(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - can_be_president_from cannot comes after can_be_president_to
        """
        association_id = 2
        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {
                "can_be_president_from": "2023-03-22",
                "can_be_president_to": "2023-03-15",
            },
            content_type="application/json",
        )
        self.assertEqual(response_president.status_code, status.HTTP_400_BAD_REQUEST)

    def test_student_patch_association_user_president(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A student president of an association can execute this request.
        - A student president of an association can update vice-president, secretary and treasurer.
        - Event is stored in History.
        - A student president of an association can add a delegation.
        """
        association_id = 2
        self.assertFalse(len(mail.outbox))
        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {
                "can_be_president_from": "2023-03-22",
                "can_be_president_to": "2023-03-29",
                "is_secretary": True,
                "is_treasurer": False,
            },
            content_type="application/json",
        )
        asso_user = AssociationUser.objects.get(user_id=self.student_user_id, association_id=association_id)
        self.assertEqual(response_president.status_code, status.HTTP_200_OK)
        self.assertEqual(History.objects.filter(action_title="ASSOCIATION_USER_DELEGATION_CHANGED").count(), 1)
        self.assertTrue(len(mail.outbox))
        self.assertEqual(asso_user.can_be_president_from, datetime.date(2023, 3, 22))
        self.assertFalse(asso_user.is_president)
        self.assertTrue(asso_user.is_secretary)
        self.assertFalse(asso_user.is_treasurer)
        self.assertFalse(asso_user.is_vice_president)

        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {
                "can_be_president_to": None,
                "is_treasurer": True,
            },
            content_type="application/json",
        )
        asso_user = AssociationUser.objects.get(user_id=self.student_user_id, association_id=association_id)
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
        asso_user = AssociationUser.objects.get(user_id=self.student_user_id, association_id=association_id)
        self.assertEqual(response_president.status_code, status.HTTP_200_OK)
        self.assertFalse(asso_user.is_president)
        self.assertFalse(asso_user.is_secretary)
        self.assertFalse(asso_user.is_treasurer)
        self.assertTrue(asso_user.is_vice_president)

    def test_student_patch_association_user_other_president(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A student president of another association cannot execute this request.
        """
        response_president = self.president_student_client.patch(
            f"/users/{self.president_user_id}/associations/3",
            {"is_secretary": True},
            content_type="application/json",
        )
        self.assertEqual(response_president.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_patch_association_user_serializer_error(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A manager can execute this request.
        - Serializer fields must be valid.
        """
        asso_user = AssociationUser.objects.get(user_id=self.president_user_id, is_president=True)
        response = self.manager_client.patch(
            f"/users/{self.president_user_id}/associations/{asso_user.association_id}",
            {"is_president": "bad format"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_patch_association_user_update_president(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A manager can execute this request.
        - Link between member and association is correctly updated.
        - Event is stored in History.
        - If giving president privileges to a member,
              the old president is no longer president of the association.
        - A manager can validate a UserAssociation link.
        - A manager can add a president to an association without one.
        """
        association_id = self.student_asso_id

        response = self.manager_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {"is_president": True},
            content_type="application/json",
        )
        asso_user = AssociationUser.objects.get(user_id=self.student_user_id, association_id=association_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(History.objects.filter(action_title="ASSOCIATION_USER_CHANGED").count(), 1)
        self.assertTrue(asso_user.is_president)

        old_president = AssociationUser.objects.get(user_id=self.president_user_id, association_id=association_id)
        self.assertFalse(old_president.is_president)

        self.assertFalse(len(mail.outbox))
        response = self.manager_client.patch(
            f"/users/{self.unvalidated_user_id}/associations/{association_id}",
            {"is_validated_by_admin": True},
            content_type="application/json",
        )
        asso_user = AssociationUser.objects.get(user_id=self.unvalidated_user_id, association_id=association_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(asso_user.is_validated_by_admin)
        self.assertTrue(len(mail.outbox))

        association_id = 5
        response = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.student_user_id,
                "association": association_id,
            },
        )
        response = self.manager_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {"is_president": True},
            content_type="application/json",
        )
        asso_user = AssociationUser.objects.get(user_id=self.student_user_id, association_id=association_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(asso_user.is_president)

    def test_manager_patch_association_user(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A manager can execute this request.
        - Link between member and association is correctly updated.
        - Event is stored in History.
        """
        asso_user = AssociationUser.objects.get(user_id=self.president_user_id, is_president=True)
        response = self.manager_client.patch(
            f"/users/{self.president_user_id}/associations/{asso_user.association_id}",
            {"is_president": False},
            content_type="application/json",
        )
        asso_user = AssociationUser.objects.get(user_id=self.president_user_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(History.objects.filter(action_title="ASSOCIATION_USER_CHANGED").count(), 1)
        self.assertFalse(asso_user.is_president)

    def test_manager_patch_association_user_404(self):
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

    def test_manager_patch_association_user_non_existing_link(self):
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

    def test_student_delete_user_association(self):
        """
        DELETE /users/{user_id}/associations/{association_id} .

        - A student user cannot execute this request.
        """
        asso_user = AssociationUser.objects.get(user_id=self.unvalidated_user_id)
        response_student = self.student_client.delete(f"/users/{self.unvalidated_user_id}/associations/{asso_user.id}")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_delete_association_user_404_user(self):
        """
        DELETE /users/{user_id}/associations/{association_id} .

        - Cannot remove link to an association from a non-existing user.
        """
        response = self.manager_client.get(f"/users/{self.student_user_id}/associations/")
        first_user_association_id = response.data[0]["id"]

        response_delete = self.manager_client.delete(f"/users/9999/associations/{str(first_user_association_id)}")
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_delete_association_user_404_association(self):
        """
        DELETE /users/{user_id}/associations/{association_id} .

        - Cannot remove link from a non-existing association to a user.
        """
        response_delete = self.manager_client.delete(f"/users/{self.student_user_id}/associations/99")
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_delete_association_user(self):
        """
        DELETE /users/{user_id}/associations/{association_id} .

        - The user must exist.
        - The association must exist.
        - A manager user can execute this request.
        - The link between an association and a user is deleted.
        """
        response = self.manager_client.get(f"/users/{self.student_user_id}/associations/")
        first_user_association_id = response.data[0]["id"]

        response_delete = self.manager_client.delete(
            f"/users/{self.student_user_id}/associations/{str(first_user_association_id)}"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            AssociationUser.objects.get(user_id=self.student_user_id, association_id=first_user_association_id)
