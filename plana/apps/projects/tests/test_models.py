"""List of tests done on projects models."""
from django.test import Client, TestCase

from plana.apps.projects.models.category import Category


class ProjectsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "projects_category.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_category_model(self):
        """There's at least one category in the database."""
        category = Category.objects.first()
        self.assertEqual(str(category), category.name)
