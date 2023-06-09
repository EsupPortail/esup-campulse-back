"""List of tests done on commissions models."""
from django.test import Client, TestCase

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_date import CommissionDate


class CommissionsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "commissions_commission.json",
        "commissions_commissiondate.json",
        "institutions_institution.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_commission_model(self):
        """There's at least one commission in the database."""
        commission = Commission.objects.first()
        self.assertEqual(str(commission), f"{commission.name} ({commission.acronym})")

    def test_commission_date_model(self):
        """There's at least one commission date in the database."""
        commission_date = CommissionDate.objects.first()
        self.assertEqual(
            str(commission_date),
            f"{commission_date.submission_date}, {commission_date.commission_date}",
        )
