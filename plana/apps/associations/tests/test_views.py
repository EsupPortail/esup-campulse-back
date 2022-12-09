"""
List of tests done on associations views.
"""
import json

from django.test import TestCase, Client

from rest_framework import status

from plana.apps.associations.models.association import Association


class AssociationsViewsTests(TestCase):
    """
    Main tests class.
    """

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "associations_socialnetwork.json",
    ]

    def setUp(self):
        """
        Start a default client used on all tests.
        """
        self.client = Client()

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
