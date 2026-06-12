"""List of tests done on user managers."""

from allauth.account.models import EmailAddress
from allauth.socialaccount.models import SocialAccount
from django.test import TestCase
from plana.apps.users.models.user import User
from plana.apps.users.provider import CASProvider


class UserManagersTests(TestCase):
    """Main tests class for User managers."""

    fixtures = [
        "tests/account_emailaddress.json",
        "associations_activityfield.json",
        "tests/associations_association.json",
        "auth_group.json",
        "auth_permission.json",
        "tests/commissions_fund.json",
        "tests/contents_setting.json",
        "tests/institutions_institution.json",
        "institutions_institutioncomponent.json",
        "mailtemplates",
        "mailtemplatevars",
        "tests/users_associationuser.json",
        "tests/users_groupinstitutionfunduser.json",
        "tests/users_user.json",
    ]

    def test_user_manager_managed_users_not_staff(self):
        """Should return an empty queryset"""
        qs = User.objects.managed_users(user=User.objects.get(username="etudiant-asso-site@mail.tld"))
        self.assertEqual(qs.count(), 0)

    def test_user_manager_managed_users_superuser(self):
        """Should return all existing users"""
        qs_superuser = User.objects.managed_users(user=User.objects.get(username="admin@admin.admin"))
        self.assertEqual(qs_superuser.count(), User.objects.all().count())

        qs_manager_general = User.objects.managed_users(user=User.objects.get(username="gestionnaire-svu@mail.tld"))
        self.assertEqual(qs_manager_general.count(), User.objects.all().count())

    def test_user_manager_managed_users_manager_institution(self):
        """
        For not CAS manager, should return users from associations managed by its institution + himself
        For CAS manager, should return users from associations managed by its institution + CAS users from any institution or group + himself
        CAS manager has funds linked to its institution, retrieve fund members from those too
        """
        qs_not_cas = User.objects.managed_users(user=User.objects.get(username="gestionnaire-uha@mail.tld")).values_list("username", flat=True)
        self.assertCountEqual(
            list(qs_not_cas),
            ["gestionnaire-uha@mail.tld","president-asso-site-etudiant-asso-hors-site-porteur-commissions@mail.tld"]
        )

        # Creating a fake CAS User for this test only
        user = User.objects.create_user(username="PatriciaCAS", email="patriciacas@unistra.fr")
        SocialAccount.objects.create(user=user, provider=CASProvider.id, uid=user.username, extra_data={})
        EmailAddress.objects.create(user=user, email="patriciacas@unistra.fr", verified=True, primary=True)

        qs_with_cas = User.objects.managed_users(user=User.objects.get(username="gestionnaire-unistra@mail.tld")).values_list("username", flat=True)
        expected_users = [
            # Self
            "gestionnaire-unistra@mail.tld",
            # Users from associations managed by its institution
            "etudiant-asso-site@mail.tld",
            "president-asso-site@mail.tld",
            # Fund members from same institution managed funds
            "membre-fsdie-idex@mail.tld",
            "membre-commissions@mail.tld",
            # CAS account
            "PatriciaCAS",
            # Special case
            "president-asso-site-etudiant-asso-hors-site-porteur-commissions@mail.tld"
        ]
        self.assertCountEqual(list(qs_with_cas), expected_users)

    def test_user_manager_managed_users_manager_misc(self):
        """
        Misc manager should return :
        - student misc users
        - users linked to its institution-managed fund
        - user from its institution-managed associations
        """
        qs_misc = User.objects.managed_users(user=User.objects.get(username="gestionnaire-crous@mail.tld")).values_list("username", flat=True)
        expected_users = [
            # Self
            "gestionnaire-crous@mail.tld",
            # Misc students
            "etudiant-porteur@mail.tld",
            "compte-presque-valide@mail.tld",
            # Users from associations managed by its institution
            "etudiant-asso-hors-site@mail.tld",
            "president-asso-hors-site@mail.tld",
            # Fund members from same institution managed funds
            "membre-culture-actions@mail.tld",
            "membre-commissions@mail.tld",
            # Special case
            "president-asso-site-etudiant-asso-hors-site-porteur-commissions@mail.tld"
        ]
        self.assertCountEqual(list(qs_misc), expected_users)
