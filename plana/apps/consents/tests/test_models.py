from django.test import TestCase, Client
from plana.apps.consents.models.consent import GDPRConsent


class GDPRConsentsModelsTests(TestCase):
    fixtures = [
        "consents_gdprconsent.json",
    ]

    def setUp(self):
        self.client = Client()

    def testConsentModel(self):
        consent = GDPRConsent.objects.first()
        self.assertEqual(str(consent), f"{consent.title}")
