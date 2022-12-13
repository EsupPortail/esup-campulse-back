"""
List of tests done on users views with an anonymous user.
"""
from django.test import Client, TestCase
from rest_framework import status

from plana.apps.users.models.association_users import AssociationUsers


class UserViewsAnonymousTests(TestCase):
    """
    Main tests class.
    """

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "associations_socialnetwork.json",
        "auth_group.json",
        "users_associationusers.json",
        "users_user.json",
    ]

    def setUp(self):
        """
        Start a default client used on all tests.
        """
        self.anonymous_client = Client()

    def test_anonymous_get_users_list(self):
        """
        GET /users/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_user_detail(self):
        """
        GET /users/{id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/2")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_patch_user_detail(self):
        """
        PATCH /users/{id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.patch(
            "/users/2", {"username": "Bienvenueg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_delete_user_detail(self):
        """
        DELETE /users/{id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.delete("/users/2")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_put_user_detail(self):
        """
        PUT /users/{id}
        - Request should return an error no matter which role is trying to execute it.
        """
        response_anonymous = self.anonymous_client.put(
            "/users/2", {"username": "Aurevoirg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_get_associations_user_list(self):
        """
        GET /users/associations/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/associations/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_association_user(self):
        """
        POST /users/associations/
        - An anonymous user cannot add a link between a validated user and an association.
        - An anonymous user can add a link between a non-validated user and an association.
        - A user cannot be added twice in the same association.
        - A non-existing user cannot be added in an association.
        - A user cannot be added in a non-existing association.
        - user field is mandatory.
        - association field is mandatory.
        """

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": "test@pas-unistra.fr",
                "association": 2,
                "has_office_status": False,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
                "association": 2,
                "has_office_status": False,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_201_CREATED)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
                "association": 2,
                "has_office_status": False,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": "george-luCAS",
                "association": 2,
                "has_office_status": False,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
                "association": 99,
                "has_office_status": False,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "association": 2,
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/associations/",
            {
                "user": "prenom.nom@adressemail.fr",
            },
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_get_associations_user_detail(self):
        """
        GET /users/associations/{user_id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/associations/2")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_delete_association_user(self):
        """
        DELETE /users/associations/{user_id}/{association_id}
        - An anonymous user cannot execute this request.
        """
        user_id = 2
        asso_user = AssociationUsers.objects.get(user_id=user_id)
        response_anonymous = self.anonymous_client.delete(
            f"/users/associations/{user_id}/{asso_user.id}"
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_auth_user_detail(self):
        """
        GET /users/auth/user/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/auth/user/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_patch_auth_user_detail(self):
        """
        PATCH /users/auth/user/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.patch(
            "/users/auth/user/", {"username": "Bienvenueg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_put_auth_user_detail(self):
        """
        PUT /users/auth/user/
        - Request should return an error no matter which role is trying to execute it.
        """
        response_anonymous = self.anonymous_client.put(
            "/users/auth/user/", {"username": "Aurevoirg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_self_consents_user_list(self):
        """
        GET /users/consents/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/consents/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_user_consents(self):
        """
        POST /users/consents/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 1}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_consents_user_list(self):
        """
        GET /users/consents/{user_id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/consents/2")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_user_groups_list(self):
        """
        GET /users/groups/
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/groups/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_user_groups(self):
        """
        POST /users/groups/
        - An anonymous user cannot add a link between a validated user and a group.
        - An anonymous user can add a link between a non-validated user and a group.
        - A non-existing user cannot be added in a group.
        - A user cannot be added in a non-existing group.
        - username field is mandatory.
        - groups field is mandatory.
        """

        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": "test@pas-unistra.fr", "groups": [1, 2]},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": "prenom.nom@adressemail.fr", "groups": [1, 2]},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_200_OK)

        response_anonymous = self.anonymous_client.post(
            "/users/groups/",
            {"username": "patricia-CAS", "groups": [1, 2]},
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.client.post("/users/groups/", {"groups": [66]})
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

        response_anonymous = self.client.post(
            "/users/groups/", {"username": "prenom.nom@adressemail.fr"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_get_user_groups_detail(self):
        """
        GET /users/groups/{user_id}
        - An anonymous user cannot execute this request.
        """
        response_anonymous = self.anonymous_client.get("/users/groups/2")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_delete_user_group(self):
        """
        DELETE /users/groups/{user_id}/{group_id}
        - An anonymous user cannot execute this request.
        """
        user_id = 2
        response_anonymous = self.client.delete(f"/users/groups/{user_id}/5")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)
