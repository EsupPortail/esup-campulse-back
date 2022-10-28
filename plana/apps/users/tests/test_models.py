from django.test import TestCase, Client
from ..models import User

class AssociationsModelsTests(TestCase):
    fixtures = ['users.json']

    def setUp(self):
        self.client = Client()


    def testUserModel(self):
        user =  User.objects.first()
        self.assertEqual(str(user), f"{user.first_name} {user.last_name}")
