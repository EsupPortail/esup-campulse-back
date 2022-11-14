from django.test import TestCase, Client
from plana.apps.users.models.user import User, AssociationUsers


class UsersModelsTests(TestCase):
    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "associations_socialnetwork.json",
        "account_emailaddress.json",
        "auth_group.json",
        "users_associationsusers.json",
        "users_user.json",
        "users_user_groups.json",
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
