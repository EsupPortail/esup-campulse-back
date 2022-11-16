import json

from django.test import TestCase, Client
from django.contrib.auth.models import Group

from django.urls import reverse
from rest_framework import status

from plana.apps.users.models.user import User, AssociationUsers


class UserTests(TestCase):
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

    def test_get_users_list(self):
        users_cnt = User.objects.count()
        self.assertTrue(users_cnt > 0)

        response = self.client.get(reverse("user_list"))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), users_cnt)

    # TODO Anonymous users aren't allowed to see user details anymore. Correct the test to pass an authenticated user.
    """
    def test_get_user_detail(self):
        user = User.objects.get(pk=7)

        response = self.client.get(reverse('user_detail', args=[1]))
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        user_1 = json.loads(response.content.decode('utf-8'))
        self.assertEqual(user_1["username"], user.username)


    def test_get_association_users_list(self):
        asso_users_cnt = AssociationUsers.objects.count()
        self.assertTrue(asso_users_cnt > 0)

        response = self.client.get("/users/associations/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), asso_users_cnt)
    """
