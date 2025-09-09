"""Test root error URLs."""

from django.test import Client, TestCase
from rest_framework import status


class RootViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "commissions_commission.json",
        "commissions_fund.json",
        "documents_document.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
    ]

    def setUp(self):
        """Start default client."""
        self.client = Client()

    def test_stats_view(self):
        response = self.client.get("/stats/")
        expected_stats = {
            "association_count": 2,
            "next_commission_date": "2099-10-20",
            "last_charter_update": "2023-03-15"
        }

        self.assertEqual(response.data, expected_stats)

    def test_root(self):
        """Base request."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_forbidden(self):
        """403 test."""
        # TODO Simulate generic 403 request.
        """
        response = self.client.get("/admin")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        """

    def test_not_found(self):
        """404 test."""
        response = self.client.get("/nothinghere")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
