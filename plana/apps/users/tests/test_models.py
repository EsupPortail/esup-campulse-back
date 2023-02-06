"""
List of tests done on users models.
"""
from django.test import Client, TestCase

from plana.apps.users.models.gdpr_consent_users import GDPRConsentUsers
from plana.apps.users.models.user import AssociationUsers, GroupInstitutionUsers, User


class UsersModelsTests(TestCase):
    """
    Main tests class.
    """

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "auth_group.json",
        "consents_gdprconsent.json",
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
        "users_associationusers.json",
        "users_gdprconsentusers.json",
        "users_groupinstitutionusers.json",
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
        The user is superuser.
        """
        user = User.objects.filter(is_superuser=True).first()
        self.assertEqual(str(user), f"{user.first_name} {user.last_name}")
        self.assertEqual(user.has_perm("bonjourg"), True)

    def test_association_users_model(self):
        """
        There's at least one user linked to an association in the database.
        The user is in the correct association.
        """
        asso_user = AssociationUsers.objects.first()
        self.assertEqual(
            str(asso_user),
            f"{asso_user.user}, {asso_user.association}, office : {asso_user.can_be_president}",
        )
        self.assertEqual(asso_user.user.is_in_association(asso_user.association), True)
        self.assertEqual(asso_user.user.is_in_association(7), False)

    def test_gdpr_consent_users_model(self):
        """
        There's at least one user linked to a GDPR consent in the database.
        """
        consent_user = GDPRConsentUsers.objects.first()
        self.assertEqual(
            str(consent_user),
            f"{consent_user.user}, {consent_user.consent}, date : {consent_user.date_consented}",
        )

    def test_group_institution_users_model(self):
        """
        There's at least one user linked to a group in the database.
        """
        group_user = GroupInstitutionUsers.objects.first()
        self.assertEqual(
            str(group_user),
            f"{group_user.user}, {group_user.group}, {group_user.institution}",
        )
