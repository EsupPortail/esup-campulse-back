"""List of tests done on associations views."""
import json

from django.test import Client, TestCase
from rest_framework import status

from plana.apps.contents.models.content import Content


class ContentsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "contents_content.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_get_contents_list(self):
        """
        GET /contents/ .

        - There's at least one content in the contents list.
        - The route can be accessed by anyone.
        - We get the same amount of contents through the model and through the view.
        - Contents details are returned (test the "code" attribute).
        - Filter by code is available.
        """
        contents_cnt = Content.objects.count()
        self.assertTrue(contents_cnt > 0)

        response = self.client.get("/contents/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), contents_cnt)

        content_1 = content[0]
        self.assertTrue(content_1.get("code"))

        code = "HOME_INFO"
        response = self.client.get(f"/contents/?code={code}")
        self.assertEqual(response.data[0]["code"], code)
