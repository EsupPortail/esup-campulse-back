"""List of tests done on logos views."""
import json

from django.test import Client, TestCase
from rest_framework import status

from plana.apps.contents.models.logo import Logo


class ContentsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "contents_logo.json",
    ]

    @classmethod
    def setUpTestData(cls):
        # Start a default client used on most tests.
        cls.client = Client()

    def test_get_contents_list(self):
        """
        GET /contents/ .

        - There's at least one logo in the logos list.
        - The route can be accessed by anyone.
        - We get the same amount of logos through the model and through the view.
        - Logos details are returned (test the "title" attribute).
        """
        logos_cnt = Logo.objects.count()
        self.assertTrue(logos_cnt > 0)

        response = self.client.get("/contents/logos")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        logo = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(logo), logos_cnt)

        logo_1 = logo[0]
        self.assertTrue(logo_1.get("title"))
