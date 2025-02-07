"""List of tests done on auth groups views."""

import json

from django.contrib.auth.models import Group
from django.test import Client, TestCase
from rest_framework import status


class GroupViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "auth_group.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_get_groups_list(self):
        """
        GET /groups/ .

        - There's at least one group in the groups list.
        - The route can be accessed by anyone.
        - We get the same amount of groups through the model and through the view.
        - Groups details are returned (test the "name" attribute).
        - Filter by name is available.
        """
        groups_cnt = Group.objects.count()

        response = self.client.get("/groups/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), groups_cnt)

        name = "MANAGER_GENERAL"
        response = self.client.get(f"/groups/?name={name}")
        self.assertEqual(response.data[0]["name"], name)
