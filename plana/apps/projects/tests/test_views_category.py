"""List of tests done on projects categories views."""
import json

from django.test import Client, TestCase
from rest_framework import status

from plana.apps.projects.models.category import Category


class ProjectsCategoriesViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "projects_category.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_get_categories_list(self):
        """
        GET /projects/categories/names .

        - There's at least one category in the categories list.
        - The route can be accessed by anyone.
        - We get the same amount of categories through the model and through the view.
        - Categories details are returned (test the "name" attribute).
        """
        categories_cnt = Category.objects.count()
        self.assertTrue(categories_cnt > 0)

        response = self.client.get("/projects/categories/names")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), categories_cnt)

        category_1 = content[0]
        self.assertTrue(category_1.get("name"))
