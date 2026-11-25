"""List of tests done on commissions models."""

from django.test import Client, TestCase

from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.fund import Fund


class CommissionsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "auth_group.json",
        "auth_permission.json",
        "tests/commissions_fund.json",
        "tests/commissions_commission.json",
        "tests/commissions_commissionfund.json",
        "tests/institutions_institution.json",
        "tests/users_groupinstitutionfunduser.json",
        "tests/users_user.json",
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

    def test_get_fund_members_emails(self):
        commission_all = Commission.objects.get(pk=1)
        emails_all = list(commission_all.get_fund_members_emails())
        self.assertCountEqual(
            emails_all,
            [
                "membre-commissions@mail.tld",
                "membre-culture-actions@mail.tld",
                "membre-fsdie-idex@mail.tld",
                "president-asso-site-etudiant-asso-hors-site-porteur-commissions@mail.tld"
            ]
        )

        commission = Commission.objects.get(pk=2)
        emails = list(commission.get_fund_members_emails())
        print(emails)
        self.assertCountEqual(
            emails,
            [
                "membre-commissions@mail.tld",
                "membre-fsdie-idex@mail.tld",
                "president-asso-site-etudiant-asso-hors-site-porteur-commissions@mail.tld"
            ]
        )
