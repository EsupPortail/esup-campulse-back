"""List of tests done on commissions views."""
import json

from django.test import Client, TestCase
from rest_framework import status

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_date import CommissionDate


class CommissionsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "commissions_commission.json",
        "commissions_commissiondate.json",
        "institutions_institution.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_get_commissions_list(self):
        """
        GET /commissions/ .

        - There's at least one commission in the commissions list.
        - The route can be accessed by anyone.
        - We get the same amount of commissions through the model and through the view.
        - Commissions details are returned (test the "name" attribute).
        """
        commissions_cnt = Commission.objects.count()
        self.assertTrue(commissions_cnt > 0)

        response = self.client.get("/commissions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commissions_cnt)

        commission_1 = content[0]
        self.assertTrue(commission_1.get("name"))

    def test_get_institution_components_list(self):
        """
        GET /commissions/commission_dates .

        - There's at least one commission date in the commission dates list.
        - The route can be accessed by anyone.
        - We get the same amount of commission dates through the model and through the view.
        """
        commission_dates_cnt = CommissionDate.objects.count()
        self.assertTrue(commission_dates_cnt > 0)

        response = self.client.get("/commissions/commission_dates")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), commission_dates_cnt)
