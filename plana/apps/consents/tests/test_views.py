import json

from django.test import TestCase, Client

from rest_framework import status

from plana.apps.consents.models.consent import GDPRConsent


class GDPRConsentsViewsTests(TestCase):
    fixtures = [
        "consents_gdprconsent.json",
    ]

    def setUp(self):
        self.client = Client()

    def test_get_consents_list(self):
        groups_cnt = GDPRConsent.objects.count()
        self.assertTrue(groups_cnt > 0)

        response = self.client.get("/consents/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), groups_cnt)

        consent_1 = content[0]
        self.assertTrue(consent_1.get("title"))
