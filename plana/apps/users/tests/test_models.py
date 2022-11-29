from django.test import TestCase, Client

from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import User


class UsersModelsTests(TestCase):
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
        self.client = Client()

    def testUserModel(self):
        user = User.objects.first()
        self.assertEqual(str(user), f"{user.first_name} {user.last_name}")

    def testAssociationUsersModel(self):
        asso_user = AssociationUsers.objects.first()
        self.assertEqual(
            str(asso_user),
            f"{asso_user.user}, {asso_user.association}, office : {asso_user.has_office_status}",
        )

    def testGDPRConsentUsersModel(self):
        consent_user = GDPRConsentUsers.objects.first()
        self.assertEqual(
            str(consent_user),
            f"{consent_user.user}, {consent_user.consent}, date : {consent_user.date_consented}",
        )
