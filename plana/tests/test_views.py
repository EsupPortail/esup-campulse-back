"""Test root error URLs."""

from django.test import Client, TestCase
from rest_framework import status


class RootViewsTests(TestCase):
    """Main tests class."""

    def setUp(self):
        """Start default client."""
        self.client = Client()

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
        response = self.client.get("/saucisse")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
