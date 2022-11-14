from django.test import TestCase, Client
from ..models import User, AssociationUsers


class AssociationsModelsTests(TestCase):
    fixtures = [
        "users.json",
        "associations_users.json",
        "associations.json",
        "institutions.json",
        "institution_components.json",
        "activity_fields.json",
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
