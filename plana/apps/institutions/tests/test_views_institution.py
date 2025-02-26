"""List of tests done on associations views."""

import json

from django.test import Client, TestCase
from rest_framework import status

from plana.apps.institutions.models.institution import Institution
from plana.apps.institutions.models.institution_component import InstitutionComponent


class AssociationsViewsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "tests/institutions_institution.json",
        "institutions_institutioncomponent.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_get_institutions_list(self):
        """
        GET /institutions/ .

        - There's at least one institution in the institutions list.
        - The route can be accessed by anyone.
        - We get the same amount of institutions through the model and through the view.
        - Institutions details are returned (test the "name" attribute).
        - Filter by acronym is available.
        """
        institutions_cnt = Institution.objects.count()
        self.assertTrue(institutions_cnt > 0)

        response = self.client.get("/institutions/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), institutions_cnt)

        institution_1 = content[0]
        self.assertTrue(institution_1.get("name"))

        acronym = "Unistra"
        response = self.client.get(f"/institutions/?acronym={acronym}")
        self.assertEqual(response.data[0]["acronym"], acronym)

    def test_get_institution_components_list(self):
        """
        GET /institutions/institution_components .

        - There's at least one institution component in the institution components list.
        - The route can be accessed by anyone.
        - We get the same amount of institution components through the model and through the view.
        - Institution components details are returned (test the "name" attribute).
        """
        institution_components_cnt = InstitutionComponent.objects.count()
        self.assertTrue(institution_components_cnt > 0)

        response = self.client.get("/institutions/institution_components")
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode("utf-8"))
        self.assertEqual(len(content), institution_components_cnt)

        institution_component_1 = content[0]
        self.assertTrue(institution_component_1.get("name"))
