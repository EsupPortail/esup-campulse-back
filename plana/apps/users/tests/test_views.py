import json

from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import User


class UserViewsTests(TestCase):
    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "associations_socialnetwork.json",
        "account_emailaddress.json",
        "consents_gdprconsent.json",
        "auth_group.json",
        "users_associationusers.json",
        "users_gdprconsentusers.json",
        "users_user.json",
        "users_user_groups.json",
    ]

    def setUp(self):
        self.client = Client()
        url = reverse("rest_login")
        data = {
            "username": "test@pas-unistra.fr",
            "password": "motdepasse",
        }
        self.response = self.client.post(url, data)
        self.home_url = reverse("home")

        self.anonymous_client = Client()

        self.manager_client = Client()
        url_manager = reverse("rest_login")
        data_manager = {
            "username": "gestionnaire-svu@mail.tld",
            "password": "motdepasse",
        }
        self.response = self.manager_client.post(url_manager, data_manager)

    # TODO Route doesn't exist anymore at this time.
    """
    def test_get_users_list(self):
        users_cnt = User.objects.count()
        self.assertTrue(users_cnt > 0)

        response = self.client.get(reverse("user_list"))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), users_cnt)
    """

    def test_get_user_detail(self):
        user = User.objects.get(pk=2)

        response = self.client.get("/users/auth/user/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        user_1 = json.loads(response.content.decode("utf-8"))
        self.assertEqual(user_1["username"], user.username)

    def test_patch_user_detail(self):
        response = self.anonymous_client.put(
            "/users/auth/user/", {"username": "Aurevoirg"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.anonymous_client.patch(
            "/users/auth/user/", {"username": "Bienvenueg"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        user = User.objects.get(pk=2)

        response = self.client.put("/users/auth/user/", {"username": "Alorsçavag"})
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        response = self.client.patch(
            "/users/auth/user/",
            data={"username": "Mafoipastropmalpourlasaisong"},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response = self.client.patch(
            "/users/auth/user/",
            data={"is_validated_by_admin": False},
            content_type="application/json",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_associations_user_list(self):
        # associations_user_cnt = AssociationUsers.objects.count()
        # self.assertTrue(associations_user_cnt > 0)

        # An anonymous user can't execute this request
        response = self.anonymous_client.get("/users/associations/2")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # A student user can't execute this request.
        response = self.client.get("/users/associations/2")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # A manager user can execute this request.
        response = self.manager_client.get("/users/associations/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_get_self_associations_user_list(self):
        # A student user can execute this request.
        response_student = self.client.get("/users/associations/")
        self.assertEqual(response_student.status_code, status.HTTP_200_OK)

        associations_user_cnt = AssociationUsers.objects.filter(user_id=2).count()
        content = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(len(content), associations_user_cnt)

        # An anonymous user can't execute this request
        response_anonymous = self.anonymous_client.get("/users/associations/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

        # A manager user can get a list of every association-user links
        associations_user_all_cnt = AssociationUsers.objects.count()
        response_all_asso = self.manager_client.get("/users/associations/")
        content_all_asso = json.loads(response_all_asso.content.decode("utf-8"))
        self.assertEqual(len(content_all_asso), associations_user_all_cnt)

    def test_link_user_to_associations(self):
        # An admin-validated user can't be added in an association
        response = self.client.post(
            "/users/associations/",
            {
                "user": "test@pas-unistra.fr",
                "association": 2,
                "has_office_status": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # A non-validated user can be added in an association
        response = self.client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
                "association": 1,
                "has_office_status": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # A user cannot be added twice in the same association
        response = self.client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
                "association": 1,
                "has_office_status": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Authentication is not needed to access view
        response = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
                "association": 2,
                "has_office_status": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # A user cannot be part of a non-existing association
        response = self.client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
                "association": 99,
                "has_office_status": False,
            },
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_get_consents_user_list(self):
        # An anonymous user can't execute this request
        response = self.anonymous_client.get("/users/consents/2")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # A student user can't execute this request.
        response = self.client.get("/users/consents/2")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # A manager user can execute this request.
        response = self.manager_client.get("/users/consents/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_self_get_consents_user_list(self):
        # An anonymous user can't execute this request
        response = self.anonymous_client.get("/users/consents/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # An authenticated user can execute this request.
        response = self.client.get("/users/consents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # A student user can execute this request and get only his consents
        consents_user_cnt = GDPRConsentUsers.objects.filter(user_id=2).count()
        response_student = self.client.get("/users/consents/")
        content_student = json.loads(response_student.content.decode("utf-8"))
        self.assertEqual(len(content_student), consents_user_cnt)

        # A manager user can get a list of every regulation consented by every user
        consents_user_all_cnt = GDPRConsentUsers.objects.count()
        response_all_consents = self.manager_client.get("/users/consents/")
        content_all_consents = json.loads(response_all_consents.content.decode("utf-8"))
        self.assertEqual(len(content_all_consents), consents_user_all_cnt)


    def test_post_user_consents(self):
        # An authenticated user can execute this request
        response = self.client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # A user can't consent mutliple times to the same regulation
        response = self.client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # An anonymous user can't execute this request
        response = self.anonymous_client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # A user cannot consent to non-existing gdpr-consent object
        response = self.client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 75}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # TODO : add rights management
    def test_get_user_groups_list(self):
        user = User.objects.get(pk=2)
        groups = list(user.groups.all().values("id", "name"))

        response = self.client.get("/users/groups/2")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        response_unauthorized = self.anonymous_client.get("/users/groups/2")
        self.assertEqual(
            response_unauthorized.status_code, status.HTTP_401_UNAUTHORIZED
        )

        get_groups = json.loads(response.content.decode("utf-8"))
        self.assertEqual(get_groups, groups)

    def test_link_user_to_groups(self):
        # Groups of admin-validated accounts can't be updated
        response = self.client.post(
            "/users/groups/", {"username": "test@pas-unistra.fr", "groups": [1, 2]}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Groups of non-validated accounts can be updated
        response = self.client.post(
            "/users/groups/",
            {"username": "prenom.nom@adressemail.fr", "groups": [1, 2]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Authentication is not needed to access view
        response = self.anonymous_client.post(
            "/users/groups/",
            {"username": "prenom.nom@adressemail.fr", "groups": [1, 2]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Cannot add a user in a non-existing group
        response = self.client.post(
            "/users/groups/", {"username": "prenom.nom@adressemail.fr", "groups": [66]}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class UserAuthTests(TestCase):
    def test_user_auth_registration(self):
        user = {
            "email": "georges.saucisse@georgeslasaucisse.fr",
            "first_name": "Georges",
            "last_name": "La Saucisse",
        }

        response = self.client.post("/users/auth/registration/", user)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.post("/users/auth/registration/", user)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
