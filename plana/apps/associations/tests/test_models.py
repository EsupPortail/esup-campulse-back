"""
List of tests done on associations models.
"""
from django.test import TestCase, Client

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association
from plana.apps.associations.models.institution import Institution
from plana.apps.associations.models.institution_component import InstitutionComponent
from plana.apps.associations.models.social_network import SocialNetwork


class AssociationsModelsTests(TestCase):
    """
    Main tests class.
    """

    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "associations_socialnetwork.json",
    ]

    def setUp(self):
        """
        Start a default client used on all tests.
        """
        self.client = Client()

    def test_association_model(self):
        """
        There's at least one association in the database.
        """
        association = Association.objects.first()
        self.assertEqual(
            str(association), f"{association.name} ({association.acronym})"
        )

    def test_social_network_model(self):
        """
        There's at least one social network linked to an association in the database.
        """
        social_network = SocialNetwork.objects.first()
        self.assertEqual(
            str(social_network), f"{social_network.type} : {social_network.location}"
        )

    def test_institution_model(self):
        """
        There's at least one institution in the database.
        """
        institution = Institution.objects.first()
        self.assertEqual(
            str(institution), f"{institution.name} ({institution.acronym})"
        )

    def test_institution_component_model(self):
        """
        There's at least one institution component in the database.
        """
        component = InstitutionComponent.objects.first()
        self.assertEqual(str(component), f"{component.name}")

    def test_activity_field_model(self):
        """
        There's at least one activity field in the database.
        """
        activity_field = ActivityField.objects.first()
        self.assertEqual(str(activity_field), f"{activity_field.name}")
