"""List of tests done on contents models."""

from django.test import Client, TestCase

from plana.apps.contents.models.content import Content
from plana.apps.contents.models.logo import Logo
from plana.apps.contents.models.setting import Setting


class ContentsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "contents_content.json",
        "contents_logo.json",
        "contents_setting.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_content_model(self):
        """There's at least one content in the database."""
        content = Content.objects.first()
        self.assertEqual(str(content), content.code)

    def test_logo_model(self):
        """There's at least one logo in the database."""
        logo = Logo.objects.first()
        self.assertEqual(str(logo), logo.acronym)

    def test_setting_model(self):
        """There's at least one setting in the database."""
        setting = Setting.objects.first()
        self.assertEqual(str(setting), setting.setting)
