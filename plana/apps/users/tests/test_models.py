"""List of tests done on users models."""

from django.test import Client, TestCase

from plana.apps.users.models.user import AssociationUser, GroupInstitutionFundUser, User


class UsersModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "associations_activityfield.json",
        "tests/associations_association.json",
        "auth_group.json",
        "tests/commissions_fund.json",
        "tests/institutions_institution.json",
        "institutions_institutioncomponent.json",
        "tests/users_associationuser.json",
        "tests/users_groupinstitutionfunduser.json",
        "tests/users_user.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_user_model(self):
        """There's at least one user in the database. The user is superuser."""
        user = User.objects.filter(is_superuser=True).first()
        self.assertEqual(str(user), f"{user.first_name} {user.last_name}")
        self.assertEqual(user.has_perm("bonjourg"), True)

    def test_association_user_model(self):
        """There's at least one user linked to the correct association in the database."""
        asso_user = AssociationUser.objects.filter(is_validated_by_admin=True).first()
        self.assertEqual(str(asso_user), f"{asso_user.user} - {asso_user.association}")
        self.assertEqual(asso_user.user.is_in_association(asso_user.association), True)
        self.assertEqual(asso_user.user.is_in_association(7), False)

    def test_group_institution_fund_user_model(self):
        """There's at least one user linked to a group in the database."""
        group_user = GroupInstitutionFundUser.objects.first()
        self.assertEqual(
            str(group_user),
            f"{group_user.user} - {group_user.group} - {group_user.institution} - {group_user.fund}",
        )
