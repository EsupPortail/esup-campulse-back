"""List of tests done on commissions views."""
import json

from django.test import Client, TestCase
from rest_framework import status

from plana.apps.commissions.models.fund import Fund


class FundsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "commissions_fund.json",
        "institutions_institution.json",
    ]

    @classmethod
    def setUpTestData(cls):
        """Start a default client used on all tests."""
        cls.client = Client()

    def test_get_funds_list(self):
        """
        GET /commissions/funds .

        - There's at least one fund in the funds list.
        - The route can be accessed by anyone.
        - We get the same amount of funds through the model and through the view.
        - Funds details are returned (test the "name" attribute).
        - Filter by acronym is available.
        """
        funds_cnt = Fund.objects.count()
        self.assertTrue(funds_cnt > 0)

        response = self.client.get("/commissions/funds/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), funds_cnt)

        fund_1 = content[0]
        self.assertTrue(fund_1.get("name"))

        acronym = "FSDIE"
        response = self.client.get(f"/commissions/funds/?acronym={acronym}")
        self.assertEqual(response.data[0]["acronym"], acronym)

        response = self.client.get("/commissions/funds/?only_next=true")
        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), funds_cnt)
