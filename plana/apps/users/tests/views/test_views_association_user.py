import datetime
import json

from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.users.models.user import AssociationUser, GroupInstitutionCommissionUser


class AssociationUserViewsTests(TestCase):
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

        # Start an anonymous client used in some tests
        cls.anonymous_client = Client()

        # Start a student client used in some tests
        cls.student_user_id = 11
        cls.student_user_name = "etudiant-asso-site@mail.tld"
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
        cls.response_president = cls.president_student_client.post(
            url_login, data_president
        )

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

    def test_anonymous_get_associations_user_list(self):
        """
        GET /users/associations/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/associations/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_get_association_user_list_global(self):
        """
        GET /users/associations/ .

        - A student user can execute this request.
        - A student user gets correct association user list data.
        """
        response_student = self.student_client.get("/users/associations/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        associations_user_cnt = AssociationUser.objects.filter(
            user_id=self.student_user_id
        ).count()
        content = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(len(content), associations_user_cnt)

    def test_student_get_association_user_list_search(self):
        """
        GET /users/associations/ .

        - A student user can execute this request.
        - A student user gets correct association user list data based on search filters.
        """
        response_president = self.president_student_client.get(
            "/users/associations/?association_id=2"
        )
        associations_user_cnt = AssociationUser.objects.filter(association_id=2).count()
        content = json.loads(response_president.content.decode("utf-8"))
        self.assertEqual(len(content), associations_user_cnt)

    def test_manager_get_association_user_list_global(self):
        """
        GET /users/associations/ .

        - A manager user can execute this request.
        - Links between user and associations are returned.
        """
        associations_user_all_cnt = AssociationUser.objects.count()
        response_all_asso = self.manager_client.get("/users/associations/")
        content_all_asso = json.loads(response_all_asso.content.decode("utf-8"))
        self.assertEqual(response_all_asso.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content_all_asso), associations_user_all_cnt)

    def test_manager_get_association_user_list_search(self):
        """
        GET /users/associations/ .

        - A manager user can execute this request.
        - Filter by is_validated_by_admin is possible.
        - Filter by institutions is possible.
        """

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
            ).values_list("id")
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

    def test_anonymous_get_association_user_detail(self):
        """
        GET /users/{user_id}/associations/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get(
            f"/users/{self.unvalidated_user_id}/associations/"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

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

        - A student user cannot execute this request.
        """
        response_student = self.student_client.get(
            f"/users/{self.unvalidated_user_id}/associations/"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_get_association_user_detail(self):
        """
        GET /users/{user_id}/associations/ .

        - A manager user can execute this request.
        - Correct data is returned.
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

    def test_get_link_association_user(self):
        """
        GET /users/{user_id}/associations/{association_id} .

        - Always returns a 405 no matter which role is trying to access it.
        """
        response_manager = self.manager_client.get("/users/999/associations/999")
        self.assertEqual(
            response_manager.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_anonymous_post_association_user_404_user(self):
        """
        POST /users/associations/ .

        - A non-existing user cannot be added in an association.
        - User param is mandatory.
        """
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
                "association": 3,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_post_association_user_404_association(self):
        """
        POST /users/associations/ .

        - A user cannot be added in a non-existing association.
        - Association param is mandatory.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 9999,
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

    def test_anonymous_post_association_user_forbidden_add(self):
        """
        POST /users/associations/ .

        - An anonymous user cannot add a link between a validated user and an association.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.student_user_name,
                "association": 2,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_post_association_user_forbidden_validate(self):
        """
        POST /users/associations/ .

        - An anonymous user cannot validate a link between a user and an association.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 5,
                "is_validated_by_admin": True,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_403_FORBIDDEN)

    def test_anonymous_post_association_user_multiple_presidents(self):
        """
        POST /users/associations/ .

        - An association cannot have two presidents.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 3,
                "is_president": True,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_post_association_user_wrong_group(self):
        """
        POST /users/associations/ .

        - Link cannot be added to a user without a group where associations can be linked.
        """
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

    def test_anonymous_post_association_user_max_members(self):
        """
        POST /users/associations/ .

        - An anonymous user cannot add a link if association is full.
        """
        association = Association.objects.get(id=5)
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

    def test_anonymous_post_association_user_success(self):
        """
        POST /users/associations/ .

        - An anonymous user can add a link between a non-validated user and an association.
        - A user cannot be added twice in the same association.
        """
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

    def test_student_post_association_user(self):
        """
        POST /users/associations/ .

        - An admin-validated student user can execute this request.
        - An admin-validated student cannot validate its own link.
        """
        self.assertFalse(len(mail.outbox))
        response_student = self.student_client.post(
            "/users/associations/",
            {
                "user": self.student_user_name,
                "association": 5,
            },
        )
        self.assertTrue(len(mail.outbox))
        self.assertEqual(response_student.status_code, status.HTTP_201_CREATED)
        user_asso = AssociationUser.objects.get(
            user_id=self.student_user_id, association_id=5
        )
        self.assertFalse(user_asso.is_validated_by_admin)

    def test_manager_misc_post_association_user_forbidden(self):
        """
        POST /users/associations/ .

        - A misc manager user cannot add an association from another institution.
        """
        response_manager_misc = self.manager_misc_client.post(
            "/users/associations/",
            {
                "user": self.student_user_name,
                "association": 1,
            },
        )
        self.assertEqual(response_manager_misc.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_post_association_user_bad_request(self):
        """
        POST /users/associations/ .

        - A manager cannot be added in an association.
        """
        response_manager = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.manager_general_user_name,
                "association": 1,
            },
        )
        self.assertEqual(response_manager.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_post_association_user(self):
        """
        POST /users/associations/ .

        - A manager user can add an association to a validated student.
        - A manager user can add an association to a non-validated student.
        """
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

    def test_put_link_association_user(self):
        """
        PUT /users/{user_id}/associations/{association_id} .

        - Always returns a 405 no matter which role is trying to access it.
        """
        response_manager = self.manager_client.put(
            "/users/999/associations/999", {"is_treasurer": True}
        )
        self.assertEqual(
            response_manager.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_anonymous_patch_association_user(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.patch(
            f"/users/{self.unvalidated_user_id}/associations/2"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

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
        asso_user = AssociationUser.objects.get(
            user_id=self.president_user_id, is_president=True
        )
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
        AssociationUser.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        response_president = self.president_student_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {"is_validated_by_admin": False},
            content_type="application/json",
        )
        AssociationUser.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
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
        asso_user = AssociationUser.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
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
        asso_user = AssociationUser.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        self.assertEqual(response_president.status_code, status.HTTP_200_OK)
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
        asso_user = AssociationUser.objects.get(
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
        asso_user = AssociationUser.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
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

    def test_student_delete_user_association(self):
        """
        DELETE /users/{user_id}/associations/{association_id} .

        - A student user cannot execute this request.
        """
        asso_user = AssociationUser.objects.get(user_id=self.unvalidated_user_id)
        response_student = self.student_client.delete(
            f"/users/{self.unvalidated_user_id}/associations/{asso_user.id}"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_delete_association_user_404_user(self):
        """
        DELETE /users/{user_id}/associations/{association_id} .

        - Cannot remove link to an association from a non-existing user.
        """
        response = self.manager_client.get(
            f"/users/{self.student_user_id}/associations/"
        )
        first_user_association_id = response.data[0]["id"]

        response_delete = self.manager_client.delete(
            f"/users/9999/associations/{str(first_user_association_id)}"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_delete_association_user_404_association(self):
        """
        DELETE /users/{user_id}/associations/{association_id} .

        - Cannot remove link from a non-existing association to a user.
        """
        response_delete = self.manager_client.delete(
            f"/users/{self.student_user_id}/associations/99"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_404_NOT_FOUND)

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
            f"/users/{self.student_user_id}/associations/{str(first_user_association_id)}"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            AssociationUser.objects.get(
                user_id=self.student_user_id, association_id=first_user_association_id
            )
