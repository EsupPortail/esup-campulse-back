import json

from allauth.socialaccount.models import SocialAccount
from django.conf import settings
from django.core import mail
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.test import Client, TestCase
from django.urls import reverse
from rest_framework import status

from plana.apps.associations.models.association import Association
from plana.apps.users.models.user import (
    AssociationUser,
    GroupInstitutionCommissionUser,
    User,
)
from plana.apps.users.provider import CASProvider


class UserViewsTests(TestCase):
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

    def test_anonymous_get_users_list(self):
        """
        GET /users/ .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

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

    def test_manager_get_users_list(self):
        """
        GET /users/ .

        - A manager user can execute this request.
        - There's at least one user in the users list.
        - We get the same amount of users through the model and through the view.
        """
        response_manager = self.manager_client.get("/users/")
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)

        users_cnt = User.objects.all().count()
        self.assertTrue(users_cnt > 0)

        content = json.loads(response_manager.content.decode("utf-8"))
        self.assertEqual(len(content), users_cnt)

    def test_manager_get_users_list_simple_queries(self):
        """
        GET /users/ .

        - is_validated_by_admin query parameter only returns a non-validated user.
        - association_id query parameter only returns users linked to this association.
        - institutions query parameter only returns users linked to these institutions.
        """
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
        links_cnt = AssociationUser.objects.filter(
            association_id=association_id
        ).count()
        self.assertEqual(len(content), links_cnt)

        institution_ids = [2, 3]
        response_manager = self.manager_client.get("/users/?institutions=2,3")
        content = json.loads(response_manager.content.decode("utf-8"))

        associations_ids = Association.objects.filter(
            institution_id__in=institution_ids
        ).values_list("id")
        links_cnt = AssociationUser.objects.filter(
            association_id__in=associations_ids
        ).count()
        self.assertEqual(len(content), links_cnt)

    def test_manager_get_users_list_advanced_queries(self):
        """
        GET /users/ .

        - Empty institutions query parameter only returns users linked to no institutions.
        - Test a mix query of users linked to institutions and users linked to no institutions.
        """
        misc_users_query = User.objects.filter(
            Q(
                id__in=GroupInstitutionCommissionUser.objects.filter(
                    institution_id__isnull=True, commission_id__isnull=True
                ).values_list("user_id")
            )
            & ~Q(id__in=AssociationUser.objects.all().values_list("user_id"))
        )
        commission_users_query = User.objects.filter(
            id__in=GroupInstitutionCommissionUser.objects.filter(
                commission_id__isnull=False
            ).values_list("user_id")
        ).values_list("id")

        response_manager = self.manager_client.get("/users/?institutions=")
        content = json.loads(response_manager.content.decode("utf-8"))
        users_query_cnt = User.objects.filter(
            Q(id__in=misc_users_query) | Q(id__in=commission_users_query)
        ).count()
        self.assertEqual(len(content), users_query_cnt)

        associations_ids = Association.objects.filter(
            institution_id__in=[2, 3]
        ).values_list("id")
        assos_users_query = AssociationUser.objects.filter(
            association_id__in=associations_ids
        ).values_list("user_id")

        response_manager = self.manager_client.get("/users/?institutions=2,3,")
        content = json.loads(response_manager.content.decode("utf-8"))
        users_query_cnt = User.objects.filter(
            Q(id__in=assos_users_query)
            | Q(id__in=misc_users_query)
            | Q(id__in=commission_users_query)
        ).count()
        self.assertEqual(len(content), users_query_cnt)

    def test_manager_get_users_list_is_cas_false(self):
        """
        GET /users/ .

        - Getting only non-cas users in the filter, only returns non-cas users.
        """
        response_manager_cas_false = self.manager_client.get("/users/?is_cas=false")
        for user in response_manager_cas_false.data:
            self.assertEqual(user["is_cas"], False)

    def test_manager_get_users_list_is_cas_true(self):
        """
        GET /users/ .

        - Getting only cas users in the filter, only returns cas users.
        """
        response_manager_cas_true = self.manager_client.get("/users/?is_cas=true")
        for user in response_manager_cas_true.data:
            self.assertEqual(user["is_cas"], True)

    def test_manager_get_users_list_filter_name(self):
        """
        GET /users/ .

        - The route can be accessed by anyone.
        - An association can be found with its name.
        """
        similar_names = [
            "Association Hors Site",
            "association hors site",
            "AssociationHorsSite",
            "associationhorssite",
            " Association Hors Site ",
            "Assôcïàtîön Hors Sité",
            "hors",
        ]
        for similar_name in similar_names:
            response = self.manager_client.get(f"/users/?name={similar_name}")
            self.assertEqual(response.data[0]["first_name"], similar_names[0])

    def test_anonymous_get_user_detail(self):
        """
        GET /users/{id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get(
            f"/users/{self.unvalidated_user_id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_manager_get_unexisting_user(self):
        """
        GET /users/{id} .

        - 404 error if user not found.
        """
        response_manager = self.manager_client.get("/users/404")
        self.assertEqual(response_manager.status_code, status.HTTP_404_NOT_FOUND)

    def test_student_get_user_detail(self):
        """
        GET /users/{id} .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.get(f"/users/{self.student_user_id}")
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

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

    def test_manager_post_user_restricted_mail(self):
        """
        POST /users/ .

        - An account with a restricted mail cannot be created.
        """
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

    def test_manager_post_user(self):
        """
        POST /users/ .

        - A manager user can execute this request.
        - The user has been created.
        - An email is received if creation is successful.
        """
        username = "bourvil@splatoon.com"
        response_manager = self.manager_client.post(
            "/users/",
            {"first_name": "Bourvil", "last_name": "André", "email": username},
        )
        self.assertEqual(response_manager.status_code, status.HTTP_201_CREATED)
        self.assertTrue(len(mail.outbox))

        user = User.objects.get(username=username)
        self.assertEqual(user.username, username)

    def test_manager_post_user_cas(self):
        """
        POST /users/ .

        - A manager user can execute this request.
        - The CAS user has been created.
        - An email is received if creation is successful.
        """
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

    def test_put_user_detail(self):
        """
        PUT /users/{id} .

        - Always returns a 405 no matter which role tries to acces it
        """
        response_manager = self.manager_client.put(
            f"/users/{self.student_user_id}", {"username": "Aurevoirg"}
        )
        self.assertEqual(
            response_manager.status_code, status.HTTP_405_METHOD_NOT_ALLOWED
        )

    def test_anonymous_patch_user_detail(self):
        """
        PATCH /users/{id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.patch(
            f"/users/{self.unvalidated_user_id}", {"username": "Bienvenueg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

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

    def test_manager_patch_user_detail_404(self):
        """
        PATCH /users/{id} .

        - A non-existing user cannot be updated.
        """
        response_manager = self.manager_client.patch(
            "/users/9999",
            data={"username": "Joséphine Ange Gardien"},
            content_type="application/json",
        )
        self.assertEqual(response_manager.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_patch_user_detail_restricted_mail(self):
        """
        PATCH /users/{id} .

        - A user cannot be patched with a restricted-domain email address.
        """
        response_manager = self.manager_client.patch(
            f"/users/{self.student_user_id}",
            data={
                "email": f"camping-paradis-cest-mieux-que-la-vie@{settings.RESTRICTED_DOMAINS[0]}"
            },
            content_type="application/json",
        )
        self.assertEqual(response_manager.status_code, status.HTTP_400_BAD_REQUEST)

    def test_manager_patch_user_detail_forbidden(self):
        """
        PATCH /users/{id} .

        - A manager user cannot edit another manager.
        """
        user_manager = User.objects.get(email=self.manager_misc_user_name)
        response_manager = self.manager_client.patch(
            f"/users/{user_manager.pk}",
            data={"email": "gestionnaire-saucisse@mail.tld"},
            content_type="application/json",
        )
        user_manager = User.objects.get(email=self.manager_misc_user_name)
        self.assertEqual(response_manager.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(user_manager.email, self.manager_misc_user_name)

    def test_manager_patch_user_detail_cas(self):
        """
        PATCH /users/{id} .

        - A manager user cannot update restricted CAS user details (ex: username, mail).
        - A manager user can validate a CAS user.
        """
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

    def test_manager_patch_user_detail_success(self):
        """
        PATCH /users/{id} .

        - A manager user can execute this request.
        - A manager user can update user details.
        - An email is received if validation is successful.
        - can_submit_projects can be set by a manager.
        """
        self.assertFalse(len(mail.outbox))
        response_manager = self.manager_client.patch(
            f"/users/{self.unvalidated_user_id}",
            data={
                "email": "aymar-venceslas@oui.org",
                "phone": "0 118 999 881 999 119 725 3",
                "is_validated_by_admin": True,
                "can_submit_projects": False,
            },
            content_type="application/json",
        )
        user = User.objects.get(pk=self.unvalidated_user_id)
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)
        self.assertEqual(user.phone, "0 118 999 881 999 119 725 3")
        self.assertEqual(user.username, "aymar-venceslas@oui.org")
        self.assertEqual(user.can_submit_projects, False)
        self.assertTrue(len(mail.outbox))

        response_manager = self.manager_client.patch(
            f"/users/{self.unvalidated_user_id}",
            data={"can_submit_projects": True},
            content_type="application/json",
        )
        self.assertEqual(response_manager.status_code, status.HTTP_200_OK)
        user = User.objects.get(pk=self.unvalidated_user_id)
        self.assertEqual(user.can_submit_projects, True)

    def test_anonymous_delete_user(self):
        """
        DELETE /users/{id} .

        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.delete(
            f"/users/{self.unvalidated_user_id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_student_delete_user(self):
        """
        DELETE /users/{id} .

        - A student user cannot execute this request.
        """
        response_student = self.student_client.delete(
            f"/users/{self.unvalidated_user_id}"
        )
        self.assertEqual(response_student.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_delete_user_404(self):
        """
        DELETE /users/{id} .

        - A non-existing user cannot be deleted.
        """
        response = self.manager_client.delete("/users/9999")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_manager_delete_user_forbidden(self):
        """
        DELETE /users/{id} .

        - A manager account cannot be deleted.
        """
        managers_ids = [1, 3, 4, 5]
        for manager_id in managers_ids:
            response = self.manager_client.delete(f"/users/{manager_id}")
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_manager_delete_user_success(self):
        """
        DELETE /users/{id} .

        - A manager user can execute this request.
        - The user has been deleted.
        - An email is received if deletion is successful.
        """
        self.assertFalse(len(mail.outbox))
        response = self.manager_client.delete(f"/users/{self.student_user_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(pk=self.student_user_id)
        self.assertTrue(len(mail.outbox))

        response = self.manager_client.delete(f"/users/{self.unvalidated_user_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(pk=self.unvalidated_user_id)

    def test_manager_delete_user_non_validated(self):
        """
        DELETE /users/{id} .

        - A manager user can execute this request.
        - An email is received if deletion is successful.
        - The non-validated account has been deleted.
        """
        self.assertFalse(len(mail.outbox))
        response = self.manager_client.delete(f"/users/{self.unvalidated_user_id}")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        with self.assertRaises(ObjectDoesNotExist):
            User.objects.get(pk=self.unvalidated_user_id)
        self.assertTrue(len(mail.outbox))
