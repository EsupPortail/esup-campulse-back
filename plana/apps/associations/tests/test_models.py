"""List of tests done on associations models."""

from django.test import Client, TestCase

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association


class AssociationsModelsTests(TestCase):
    """Main tests class."""

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "tests/institutions_institution.json",
        "institutions_institutioncomponent.json",
    ]

    def setUp(self):
        """Start a default client used on all tests."""
        self.client = Client()

    def test_association_model(self):
        """There's at least one association in the database."""
        association = Association.objects.first()
        self.assertEqual(str(association), association.acronym)

    def test_activity_field_model(self):
        """There's at least one activity field in the database."""
        activity_field = ActivityField.objects.first()
        self.assertEqual(str(activity_field), activity_field.name)
