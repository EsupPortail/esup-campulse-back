import json

from django.test import TestCase, Client
from django.contrib.auth.models import Group

from rest_framework import status

from ..models import User, AssociationUsers

class UserTests(TestCase):
    fixtures = ['users.json', 'associations_users.json', 'associations.json', 'institutions.json',
                'institution_components.json', 'activity_fields.json', 'auth_groups.json']

    def setUp(self):
        self.client = Client()

    def test_get_users_list(self):
        users_cnt = User.objects.count()
        self.assertTrue(users_cnt > 0)

        response = self.client.get('/users/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(content), users_cnt)


    def test_get_user_detail(self):
        user = User.objects.get(pk=1)

        response = self.client.get('/users/1')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        user_1 = json.loads(response.content.decode('utf-8'))
        self.assertEqual(user_1["username"], user.username)


    def test_get_association_users_list(self):
        asso_users_cnt = AssociationUsers.objects.count()
        self.assertTrue(asso_users_cnt > 0)

        response = self.client.get('/users/association/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(content), asso_users_cnt)


    def test_get_groups_list(self):
        groups_cnt = Group.objects.count()
        self.assertTrue(groups_cnt > 0)

        response = self.client.get('/users/groups/')
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode('utf-8'))
        self.assertEqual(len(content), groups_cnt)

