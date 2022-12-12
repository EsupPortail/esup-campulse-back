"""
List of tests done on users models.
"""
from django.test import Client, TestCase

from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import User


class UsersModelsTests(TestCase):
    """
    Main tests class.
    """

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "consents_gdprconsent.json",
        "users_associationusers.json",
        "users_gdprconsentusers.json",
        "users_user.json",
    ]

    def setUp(self):
        """
        Start a default client used on all tests.
        """
        self.client = Client()

    def test_user_model(self):
        """
        There's at least one user in the database.
        """
        user = User.objects.first()
        self.assertEqual(str(user), f"{user.first_name} {user.last_name}")

    def test_association_users_model(self):
        """
        There's at least one user linked to an association in the database.
        """
        asso_user = AssociationUsers.objects.first()
        self.assertEqual(
            str(asso_user),
            f"{asso_user.user}, {asso_user.association}, office : {asso_user.has_office_status}",
        )

    def test_gdpr_consent_users_model(self):
        """
        There's at least one user linked to a GDPR consent in the database.
        """
        consent_user = GDPRConsentUsers.objects.first()
        self.assertEqual(
            str(consent_user),
            f"{consent_user.user}, {consent_user.consent}, date : {consent_user.date_consented}",
        )
