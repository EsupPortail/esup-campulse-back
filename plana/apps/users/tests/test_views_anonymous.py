from django.test import TestCase, Client

from rest_framework import status

from plana.apps.users.models.association_users import AssociationUsers


class UserViewsAnonymousTests(TestCase):
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
        self.anonymous_client = Client()

    def test_anonymous_get_users_list(self):
        # An anonymous user cannot execute this request
        response_anonymous = self.anonymous_client.get("/users/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_user_detail(self):
        # An anonymous user cannot execute this request
        response_anonymous = self.anonymous_client.get("/users/2")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_patch_user_detail(self):
        # An anonymous user cannot execute this request
        response_anonymous = self.anonymous_client.patch(
            "/users/2", {"username": "Bienvenueg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_put_user_detail_404(self):
        # Request should return an error 404 no matter which role is trying to execute it
        response_anonymous = self.anonymous_client.put(
            "/users/2", {"username": "Aurevoirg"}
        )
        self.assertEqual(response_anonymous.status_code, status.HTTP_404_NOT_FOUND)

    def test_anonymous_put_auth_user_detail(self):
        # An anonymous user cannot execute this request
        response = self.anonymous_client.put(
            "/users/auth/user/", {"username": "Aurevoirg"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_patch_auth_user_detail(self):
        # An anonymous user cannot execute this request
        response = self.anonymous_client.patch(
            "/users/auth/user/", {"username": "Bienvenueg"}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_associations_user_list(self):
        # An anonymous user can't execute this request
        response = self.anonymous_client.get("/users/associations/2")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_self_associations_user_list(self):
        # An anonymous user can't execute this request
        response_anonymous = self.anonymous_client.get("/users/associations/")
        self.assertEqual(response_anonymous.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_link_user_to_associations(self):
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

    def test_anonymous_delete_user_association(self):
        # An anonymous user can't execute this request
        user_id = 2
        asso_user = AssociationUsers.objects.get(user_id=user_id)
        response = self.anonymous_client.delete(
            f"/users/associations/{user_id}/{asso_user.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_consents_user_list(self):
        # An anonymous user can't execute this request
        response = self.anonymous_client.get("/users/consents/2")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_self_consents_user_list(self):
        # An anonymous user can't execute this request
        response = self.anonymous_client.get("/users/consents/")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_post_user_consents(self):
        # An anonymous user can't execute this request
        response = self.anonymous_client.post(
            "/users/consents/", {"user": "prenom.nom@adressemail.fr", "consent": 1}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_get_user_groups_list(self):
        # An anonymous user can't execute this request
        response_unauthorized = self.anonymous_client.get("/users/groups/2")
        self.assertEqual(
            response_unauthorized.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_anonymous_get_self_user_groups_list(self):
        # An anonymous user can't execute this request
        response_unauthorized = self.anonymous_client.get("/users/groups/")
        self.assertEqual(
            response_unauthorized.status_code, status.HTTP_401_UNAUTHORIZED
        )

    def test_anonymous_delete_user_group(self):
        # A student user can't execute this request.
        user_id = 2
        response = self.client.delete(f"/users/groups/{user_id}/5")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_anonymous_link_user_to_groups(self):
        # Authentication is not needed to access view
        response = self.anonymous_client.post(
            "/users/groups/",
            {"username": "prenom.nom@adressemail.fr", "groups": [1, 2]},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
