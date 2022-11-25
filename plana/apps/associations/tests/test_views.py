import json

from django.test import TestCase, Client
from rest_framework import status

from plana.apps.associations.models.association import Association


class AssociationsViewsTests(TestCase):
    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "associations_socialnetwork.json",
    ]

    def setUp(self):
        self.client = Client()

    def test_get_associations_list(self):
        associations_cnt = Association.objects.count()
        self.assertTrue(associations_cnt > 0)

        response = self.client.get("/associations/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), associations_cnt)

        association_1 = content[0]
        self.assertTrue(association_1.get("name"))
        self.assertFalse(association_1.get("activities"))

    def test_get_association_detail(self):
        association = Association.objects.get(pk=1)

        response = self.client.get("/associations/1")
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        association_1 = json.loads(response.content.decode("utf-8"))
        self.assertEqual(association_1["name"], association.name)
        self.assertEqual(association_1["activities"], association.activities)

    def test_get_association_detail_error(self):
        not_found_response = self.client.get("/associations/50")
        self.assertEquals(not_found_response.status_code, status.HTTP_404_NOT_FOUND)
