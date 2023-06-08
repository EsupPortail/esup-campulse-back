"""List of tests done on associations models."""
from django.test import Client, TestCase

from plana.apps.institutions.models.institution import Institution
from plana.apps.institutions.models.institution_component import InstitutionComponent


class AssociationsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "institutions_institution.json",
        "institutions_institutioncomponent.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_institution_model(self):
        """There's at least one institution in the database."""
        institution = Institution.objects.first()
        self.assertEqual(
            str(institution), f"{institution.name} ({institution.acronym})"
        )

    def test_institution_component_model(self):
        """There's at least one institution component in the database."""
        component = InstitutionComponent.objects.first()
        self.assertEqual(str(component), f"{component.name} ({component.institution})")
