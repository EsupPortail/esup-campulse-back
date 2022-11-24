import json

from django.test import TestCase, Client
from plana.apps.consents.models.consent import GDPRConsent

from rest_framework import status


class GDPRConsentsTests(TestCase):
    fixtures = [
        "consents_gdprconsent.json",
    ]

    def setUp(self):
        self.client = Client()

    def test_get_groups_list(self):
        groups_cnt = GDPRConsent.objects.count()
        self.assertTrue(groups_cnt > 0)

        response = self.client.get("/consents/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), groups_cnt)
