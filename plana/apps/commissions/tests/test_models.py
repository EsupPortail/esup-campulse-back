"""List of tests done on commissions models."""
from django.test import Client, TestCase

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.fund import Fund


class CommissionsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "commissions_fund.json",
        "commissions_commission.json",
        "institutions_institution.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_fund_model(self):
        """There's at least one fund in the database."""
        fund = Fund.objects.first()
        self.assertEqual(str(fund), fund.acronym)

    def test_commission_model(self):
        """There's at least one commission in the database."""
        commission = Commission.objects.first()
        self.assertEqual(str(commission), commission.name)
