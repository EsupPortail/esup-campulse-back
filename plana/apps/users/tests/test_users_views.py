import json

from django.test import TestCase, Client
from rest_framework import status

from ..models import User

class UserTests(TestCase):
    fixtures = ['users.json']

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

