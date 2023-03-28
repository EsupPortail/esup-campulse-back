"""List of tests done on users views with a manager user."""
import json

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Q
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association

# from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import (
    AssociationUsers,
    GroupInstitutionCommissionUsers,
    User,
)
from plana.apps.users.provider import CASProvider


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
        "consents_gdprconsent.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "users_associationusers.json",
        "users_gdprconsentusers.json",
        "users_groupinstitutioncommissionusers.json",
        "users_user.json",
    ]

    def setUp(self):
        """Start a default client used on all tests, retrieves a manager user."""
        self.unvalidated_user_id = 2
        self.unvalidated_user_name = "compte-non-valide@mail.tld"
        self.student_user_id = 11
        self.student_user_name = "etudiant-asso-site@mail.tld"
        self.president_user_id = 13
        self.president_user_name = "president-asso-site@mail.tld"

        self.manager_misc_user_id = 5
        self.manager_misc_user_name = "gestionnaire-crous@mail.tld"
        self.manager_misc_client = Client()
        url_manager_misc = reverse("rest_login")
        data_manager_misc = {
            "username": self.manager_misc_user_name,
            "password": "motdepasse",
        }
        self.response = self.manager_misc_client.post(
            url_manager_misc, data_manager_misc
        )

        self.manager_general_user_id = 3
        self.manager_general_user_name = "gestionnaire-svu@mail.tld"
        self.manager_client = Client()
        url_manager = reverse("rest_login")
        data_manager = {
            "username": self.manager_general_user_name,
            "password": "motdepasse",
        }
        self.response = self.manager_client.post(url_manager, data_manager)

    def test_manager_get_users_list(self):
        """
        GET /users/ .

        - A manager user can execute this request.
        - There's at least one user in the users list.
        - We get the same amount of users through the model and through the view.
        - is_validated_by_admin query parameter only returns a non-validated user.
        - association_id query parameter only returns users linked to this association.
        - institutions query parameter only returns users linked to these institutions.
        - Empty institutions query parameter only returns users linked to no institutions.
        - Test a mix of the two last conditions.
        """
        response_manager = self.manager_client.get("/users/")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        users_cnt = User.objects.all().count()
        self.assertTrue(users_cnt > 0)

        content = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(len(content), users_cnt)

        response_manager = self.manager_client.get(
            "/users/?is_validated_by_admin=false"
        )
        for user in response_manager.data:
            self.assertEqual(user["is_validated_by_admin"], False)

        association_id = 2
        response_manager = self.manager_client.get(
            f"/users/?association_id={association_id}"
        )
        content = json.loads(response_manager.content.decode("utf-8"))
        links_cnt = AssociationUsers.objects.filter(
            association_id=association_id
        ).count()
        self.assertEqual(len(content), links_cnt)

        institution_ids = [2, 3]
        response_manager = self.manager_client.get("/users/?institutions=2,3")
        content = json.loads(response_manager.content.decode("utf-8"))

        associations_ids = Association.objects.filter(
            institution_id__in=institution_ids
        ).values_list("id", flat=True)
        links_cnt = AssociationUsers.objects.filter(
            association_id__in=associations_ids
        ).count()
        self.assertEqual(len(content), links_cnt)

        multiple_groups_users_query = (
            User.objects.annotate(num_groups=Count("groupinstitutioncommissionusers"))
            .filter(num_groups__gt=1)
            .values_list("id", flat=True)
        )
        commission_users_query = User.objects.filter(
            id__in=GroupInstitutionCommissionUsers.objects.filter(
                commission_id__isnull=False
            ).values_list("user_id", flat=True)
        ).values_list("id", flat=True)

        response_manager = self.manager_client.get("/users/?institutions=")
        content = json.loads(response_manager.content.decode("utf-8"))
        users_query_cnt = User.objects.filter(
            Q(id__in=multiple_groups_users_query) | Q(id__in=commission_users_query)
        ).count()
        self.assertEqual(len(content), users_query_cnt)

        associations_ids = Association.objects.filter(
            institution_id__in=[2, 3]
        ).values_list("id", flat=True)
        assos_users_query = AssociationUsers.objects.filter(
            association_id__in=associations_ids
        ).values_list("user_id", flat=True)

        response_manager = self.manager_client.get("/users/?institutions=2,3,")
        content = json.loads(response_manager.content.decode("utf-8"))
        users_query_cnt = User.objects.filter(
            Q(id__in=assos_users_query)
            | Q(id__in=multiple_groups_users_query)
            | Q(id__in=commission_users_query)
        ).count()
        self.assertEqual(len(content), users_query_cnt)

    def test_manager_get_users_list_is_cas(self):
        """
        GET /users/ .

        - Getting only non-cas users in the filter, only returns non-cas users.
        - Getting only cas users in the filter, only returns cas users.
        """
        response_manager_cas_false = self.manager_client.get("/users/?is_cas=false")
        for user in response_manager_cas_false.data:
            self.assertEqual(user["is_cas"], False)

        response_manager_cas_true = self.manager_client.get("/users/?is_cas=true")
        for user in response_manager_cas_true.data:
            self.assertEqual(user["is_cas"], True)

    def test_manager_post_user(self):
        """
        POST /users/ .

        - An account with a restricted mail cannot be created.
        - A manager user can execute this request.
        - The user has been created.
        - An email is received if creation is successful.
        - A CAS user can be created.
        """
        self.assertFalse(len(mail.outbox))

        response_manager = self.manager_client.post(
            "/users/",
            {
                "first_name": "Poin-Poin-Poin-Poin-Poin",
                "last_name": "Vicetone",
                "email": f"astronomia@{settings.RESTRICTED_DOMAINS[0]}",
            },
        )
        self.assertEqual(response_manager.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(len(mail.outbox))

        username = "bourvil@splatoon.com"
        response_manager = self.manager_client.post(
            "/users/",
            {"first_name": "Bourvil", "last_name": "André", "email": username},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(mail.outbox))

        user = User.objects.get(username=username)
        self.assertEqual(user.username, username)

        username = "opaline"
        email = "opaline@unistra.fr"
        response_manager = self.manager_client.post(
            "/users/",
            {
                "first_name": "Opaline",
                "last_name": "Gropif",
                "username": username,
                "email": email,
                "is_cas": True,
            },
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(mail.outbox))

        user = SocialAccount.objects.get(uid=username)
        self.assertEqual(user.uid, username)

    def test_manager_get_user_detail(self):
        """
        GET /users/{id} .

        - A manager user can execute this request.
        - User details are returned (test the "username" attribute).
        """
        response_manager = self.manager_client.get(f"/users/{self.student_user_id}")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        user = User.objects.get(pk=self.student_user_id)
        user_requested = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(user_requested["username"], user.username)

    def test_manager_patch_user_detail(self):
        """
        PATCH /users/{id} .

        - A manager user can execute this request.
        - A manager user can update user details.
        - An email is received if validation is successful.
        - A non-existing user cannot be updated.
        - Some email addresses should not be used for update.
        - A manager user cannot update restricted CAS user details.
        - A manager user can validate a CAS user.
        - A manager user cannot edit another manager.
        """
        self.assertFalse(len(mail.outbox))
        response_manager = self.manager_client.patch(
            f"/users/{self.student_user_id}",
            data={
                "email": "aymar-venceslas@oui.org",
                "phone": "0 118 999 881 999 119 725 3",
                "is_validated_by_admin": True,
            },
            content_type="application/json",
        )
        user = User.objects.get(pk=self.student_user_id)
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)
        self.assertEqual(user.phone, "0 118 999 881 999 119 725 3")
        self.assertEqual(user.username, "aymar-venceslas@oui.org")
        self.assertTrue(len(mail.outbox))

        response_manager = self.manager_client.patch(
            "/users/1000",
            data={"username": "Joséphine Ange Gardien"},
            content_type="application/json",
        )
        self.assertEqual(response_manager.status_code, status.HTTP_400_BAD_REQUEST)

        response_manager = self.manager_client.patch(
            f"/users/{self.student_user_id}",
            data={
                "email": f"camping-paradis-cest-mieux-que-la-vie@{settings.RESTRICTED_DOMAINS[0]}"
            },
            content_type="application/json",
        )
        self.assertEqual(response_manager.status_code, status.HTTP_400_BAD_REQUEST)

        user = User.objects.create_user(
            username="PatriciaCAS",
            password="pbkdf2_sha256$260000$H2vwf1hYXyooB1Qhsevrk6$ISSNgBZtbGWwNL6TSktlDCeGfd5Ib9F3c9DkKhYkZMQ=",
            email="test@unistra.fr",
        )
        SocialAccount.objects.create(
            user=user,
            provider=CASProvider.id,
            uid=user.username,
            extra_data={},
        )

        user_cas = User.objects.get(username="PatriciaCAS")
        self.manager_client.patch(
            f"/users/{user_cas.pk}",
            data={
                "username": "JesuisCASg",
                "email": "coincoincoing@zut.com",
                "is_validated_by_admin": True,
            },
            content_type="application/json",
        )
        user_cas = User.objects.get(username="PatriciaCAS")
        self.assertEqual(user_cas.is_validated_by_admin, True)
        self.assertEqual(user_cas.email, "test@unistra.fr")

        user_manager = User.objects.get(email=self.manager_misc_user_name)
        response_manager = self.manager_client.patch(
            f"/users/{user_manager.pk}",
            data={"email": "gestionnaire-saucisse@mail.tld"},
            content_type="application/json",
        )
        user_manager = User.objects.get(email=self.manager_misc_user_name)
        self.assertEqual(response_manager.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(user_manager.email, self.manager_misc_user_name)

    def test_manager_delete_user_detail(self):
        """
        DELETE /users/{id} .

        - A manager user can execute this request.
        - A user can be deleted.
        - An email is received if deletion is successful.
        - A non-existing user cannot be deleted.
        - A manager account cannot be deleted.
        - A non-validated account can be deleted.
        """
        self.assertFalse(len(mail.outbox))
        response = self.manager_client.delete(f"/users/{self.student_user_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(pk=self.student_user_id)
        self.assertTrue(len(mail.outbox))

        response = self.manager_client.delete(f"/users/{self.student_user_id}")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        managers_ids = [1, 3, 4, 5]
        for manager_id in managers_ids:
            response = self.manager_client.delete(f"/users/{manager_id}")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.manager_client.delete(f"/users/{self.unvalidated_user_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(pk=self.unvalidated_user_id)

    def test_manager_put_user_detail(self):
        """
        PUT /users/{id} .

        - Request should return an error no matter which role is trying to execute it.
        """
        response_manager = self.manager_client.put(
            f"/users/{self.student_user_id}", {"username": "Aurevoirg"}
        )
        self.assertEqual(
            response_manager.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_manager_get_associations_user_list(self):
        """
        GET /users/associations/ .

        - A manager user can execute this request.
        - Links between user and associations are returned.
        - Filter by is_validated_by_admin is possible.
        - Filter by institutions is possible.
        """
        associations_user_all_cnt = AssociationUsers.objects.count()
        response_all_asso = self.manager_client.get("/users/associations/")
        content_all_asso = json.loads(response_all_asso.content.decode("utf-8"))
        self.assertEqual(response_all_asso.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content_all_asso), associations_user_all_cnt)

        associations_user_validated_cnt = AssociationUsers.objects.filter(
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
        associations_user_institutions_cnt = AssociationUsers.objects.filter(
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
                "can_be_president": False,
            },
        )
        self.assertEqual(response_manager_misc.status_code, status.HTTP_400_BAD_REQUEST)

        response_manager = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.student_user_name,
                "association": 1,
                "can_be_president": False,
            },
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)

        response_manager = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.unvalidated_user_name,
                "association": 1,
                "can_be_president": False,
            },
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)

        response_manager = self.manager_client.post(
            "/users/associations/",
            {
                "user": self.manager_general_user_name,
                "association": 1,
                "can_be_president": True,
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

        user_associations = AssociationUsers.objects.filter(
            user_id=self.student_user_id
        )
        user_associations_requested = json.loads(
            response_manager.content.decode("utf-8")
        )
        self.assertEqual(len(user_associations_requested), len(user_associations))

    def test_manager_patch_association_users_update_president(self):
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
        asso_user = AssociationUsers.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        response = self.manager_client.patch(
            f"/users/{self.student_user_id}/associations/{association_id}",
            {"is_president": True},
            content_type="application/json",
        )
        asso_user = AssociationUsers.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(asso_user.is_president)

        old_president = AssociationUsers.objects.get(
            user_id=self.president_user_id, association_id=association_id
        )
        self.assertFalse(old_president.is_president)

        self.assertFalse(len(mail.outbox))
        response = self.manager_client.patch(
            f"/users/{self.unvalidated_user_id}/associations/{association_id}",
            {"is_validated_by_admin": True},
            content_type="application/json",
        )
        asso_user = AssociationUsers.objects.get(
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
        asso_user = AssociationUsers.objects.get(
            user_id=self.student_user_id, association_id=association_id
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(asso_user.is_president)

    def test_manager_patch_association_users(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - A manager can execute this request.
        - Link between member and association is correctly updated.
        """
        asso_user = AssociationUsers.objects.get(
            user_id=self.president_user_id, is_president=True
        )
        response = self.manager_client.patch(
            f"/users/{self.president_user_id}/associations/{asso_user.association_id}",
            {"is_president": False},
            content_type="application/json",
        )
        asso_user = AssociationUsers.objects.get(user_id=self.president_user_id)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(asso_user.is_president)

    def test_manager_patch_association_users_unexisting_params(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - Returns a bad request if non-existing user or association in parameters.
        """
        response = self.manager_client.patch(
            "/users/999/associations/999",
            {"is_secretary": True},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_patch_association_users_unexisting_link(self):
        """
        PATCH /users/{user_id}/associations/{association_id} .

        - Returns a bad request if non-existing link between selected user and association.
        """
        response = self.manager_client.patch(
            f"/users/{self.student_user_id}/associations/3",
            {"is_treasurer": True},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_delete_association_users(self):
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
        self.assertEqual(response_delete.status_code, status.HTTP_400_BAD_REQUEST)

        response_delete = self.manager_client.delete(
            f"/users/{self.student_user_id}/associations/99"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_400_BAD_REQUEST)

        response_delete = self.manager_client.delete(
            f"/users/{self.student_user_id}/associations/{str(first_user_association_id)}"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            AssociationUsers.objects.get(
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

    def test_manager_get_consents_user_list(self):
        """
        GET /users/consents/ .

        - A manager user can execute this request.
        """
        """
        consents_user_all_cnt = GDPRConsentUsers.objects.count()
        response_all_consents = self.manager_client.get("/users/consents/")
        content_all_consents = json.loads(response_all_consents.content.decode("utf-8"))
        self.assertEqual(response_all_consents.status_code, status.HTTP_200_OK)
        self.assertEqual(len(content_all_consents), consents_user_all_cnt)
        """

    def test_manager_get_consents_user_detail(self):
        """
        GET /users/consents/{user_id} .

        - A manager user can execute this request.
        - We get the same amount of consents through the model and through the view.
        """
        """
        response_manager = self.manager_client.get(
            f"/users/consents/{self.student_user_id}"
        )
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        user_consents = GDPRConsentUsers.objects.filter(user_id=self.student_user_id)
        user_consents_requested = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(len(user_consents_requested), len(user_consents))
        """

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
        - Groups for a manager can be changed.
        - Groups for a general manager can't be changed by another manager.
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

        response_manager = self.manager_client.post(
            "/users/groups/",
            {"username": self.manager_general_user_name, "group": 6},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        response_manager = self.manager_misc_client.post(
            "/users/groups/",
            {"username": self.manager_general_user_name, "group": 4},
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
        self.assertEqual(response_delete.status_code, status.HTTP_400_BAD_REQUEST)

        response_delete = self.manager_client.delete("/users/10/groups/5")
        self.assertEqual(response_delete.status_code, status.HTTP_400_BAD_REQUEST)

        AssociationUsers.objects.filter(user_id=user_id).delete()
        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_400_BAD_REQUEST)

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
        self.assertEqual(response_delete.status_code, status.HTTP_400_BAD_REQUEST)

        response_delete = self.manager_misc_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/commissions/1"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_400_BAD_REQUEST)

        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/commissions/1"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/commissions/1"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_400_BAD_REQUEST)

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
        GroupInstitutionCommissionUsers.objects.create(
            user_id=user_id, group_id=2, institution_id=4
        )
        GroupInstitutionCommissionUsers.objects.filter(
            user_id=user_id, commission_id__isnull=False
        ).delete()
        response = self.manager_client.get(f"/users/{user_id}/groups/")
        first_user_group_id = response.data[0]["group"]
        second_user_group_id = response.data[1]["group"]

        response_delete = self.manager_client.delete(
            f"/users/99/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_400_BAD_REQUEST)

        response_delete = self.manager_misc_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(response_delete.status_code, status.HTTP_400_BAD_REQUEST)

        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_204_NO_CONTENT)

        first_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(first_user_group_id)}/institutions/3"
        )
        self.assertEqual(first_response_delete.status_code, status.HTTP_400_BAD_REQUEST)

        second_response_delete = self.manager_client.delete(
            f"/users/{user_id}/groups/{str(second_user_group_id)}/institutions/4"
        )
        self.assertEqual(
            second_response_delete.status_code, status.HTTP_400_BAD_REQUEST
        )
