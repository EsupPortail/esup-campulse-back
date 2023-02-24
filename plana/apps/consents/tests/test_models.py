"""List of tests done on GDPR consents models."""
from django.test import Client, TestCase

from plana.apps.consents.models.consent import GDPRConsent


class GDPRConsentsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "consents_gdprconsent.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_consent_model(self):
        """There's at least one GDPR consent in the database."""
        consent = GDPRConsent.objects.first()
        self.assertEqual(str(consent), f"{consent.title}")
