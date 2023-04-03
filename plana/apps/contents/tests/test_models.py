"""List of tests done on contents models."""
from django.test import Client, TestCase

from plana.apps.contents.models.content import Content


class ContentsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "contents_content.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_content_model(self):
        """There's at least one content in the database."""
        content = Content.objects.first()
        self.assertEqual(str(content), f"{content.code} : {content.label}")
