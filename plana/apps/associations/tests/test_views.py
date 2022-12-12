"""
List of tests done on associations views.
"""
import json

from django.test import TestCase, Client
from django.urls import reverse

from rest_framework import status

from plana.apps.associations.models.association import Association


class AssociationsViewsTests(TestCase):
    """
    Main tests class.
    """

    fixtures = [
        "account_emailaddress.json",
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "associations_socialnetwork.json",
        "auth_group.json",
        "users_user.json",
        "users_user_groups.json",
    ]

    def setUp(self):
        """
        Start a default client used on all tests.
        """
        self.client = Client()

        self.crous_client = Client()
        url_crous = reverse("rest_login")
        data_crous = {
            "username": "gestionnaire-crous@mail.tld",
            "password": "motdepasse",
        }
        self.response = self.crous_client.post(url_crous, data_crous)

        self.svu_client = Client()
        url_svu = reverse("rest_login")
        data_svu = {
            "username": "gestionnaire-svu@mail.tld",
            "password": "motdepasse",
        }
        self.response = self.svu_client.post(url_svu, data_svu)

    def test_get_associations_list(self):
        """
        GET /associations/
        - There's at least one association in the associations list.
        - The route can be accessed by anyone.
        - We get the same amount of associations through the model and through the view.
        - Main associations details are returned (test the "name" attribute).
        - All associations details aren't returned (test the "activities" attribute).
        """
        associations_cnt = Association.objects.count()
        self.assertTrue(associations_cnt > 0)

        response = self.client.get("/associations/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), associations_cnt)

        association_1 = content[0]
        self.assertTrue(association_1.get("name"))
        self.assertFalse(association_1.get("activities"))

    def test_post_association(self):
        """
        POST /associations/
        - A SVU manager can add an association.
        - A Crous manager cannot add an association.
        - Another user cannot add an association.
        """
        response_svu = self.svu_client.post(
            "/associations/",
            {
                "name": "Les Fans de Georges la Saucisse",
            },
        )
        self.assertEqual(response_svu.status_code, status.HTTP_201_CREATED)

        response_crous = self.crous_client.post(
            "/associations/",
            {
                "name": "C'est Brice de Nice qui se connecte via CAS, il clique sur Connexion et c'est CASsé.",
            },
        )
        self.assertEqual(response_crous.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post(
            "/associations/",
            {
                "name": "Quelle chanteuse peut se connecter sans compte à l'application ? Patricia CAS.",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_association_retrieve(self):
        """
        GET /associations/{id}
        - The route can be accessed by anyone.
        - Main association details are returned (test the "name" attribute).
        - All associations details are returned (test the "activities" attribute).
        - A non-existing association can't be returned.
        """
        association = Association.objects.get(pk=1)

        response = self.client.get("/associations/1")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        association_1 = json.loads(response.content.decode("utf-8"))
        self.assertEqual(association_1["name"], association.name)
        self.assertEqual(association_1["activities"], association.activities)

        not_found_response = self.client.get("/associations/50")
        self.assertEqual(not_found_response.status_code, status.HTTP_404_NOT_FOUND)
