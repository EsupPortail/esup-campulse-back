import json

from django.test import TestCase, Client
from django.contrib.auth.models import Group

from rest_framework import status


class GroupViewsTests(TestCase):
    fixtures = [
        "auth_group.json",
    ]

    def setUp(self):
        self.client = Client()

    def test_get_groups_list(self):
        groups_cnt = Group.objects.count()
        self.assertTrue(groups_cnt > 0)

        response = self.client.get("/groups/")
        self.assertEquals(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), groups_cnt)
