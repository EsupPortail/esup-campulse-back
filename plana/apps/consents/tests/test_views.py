"""List of tests done on GDPR consents views."""
import json

from django.test import Client, TestCase
from rest_framework import status

from plana.apps.consents.models.consent import GDPRConsent


class GDPRConsentsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "consents_gdprconsent.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_get_consents_list(self):
        """
        GET /consents/ .

        - There's at least one consent in the consents list.
        - The route can be accessed by anyone.
        - We get the same amount of consents through the model and through the view.
        - Consents details are returned (test the "title" attribute).
        """
        consents_cnt = GDPRConsent.objects.count()
        self.assertTrue(consents_cnt > 0)

        response = self.client.get("/consents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), consents_cnt)

        consent_1 = content[0]
        self.assertTrue(consent_1.get("title"))
