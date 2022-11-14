from django.test import TestCase, Client
from ..models import (
    Association,
    SocialNetwork,
    Institution,
    InstitutionComponent,
    ActivityField,
)


class AssociationsModelsTests(TestCase):
    fixtures = [
        "institutions.json",
        "institution_components.json",
        "activity_fields.json",
        "associations.json",
        "social_networks.json",
    ]

    def setUp(self):
        self.client = Client()

    def testAssociationModel(self):
        association = Association.objects.first()
        self.assertEqual(
            str(association), f"{association.name} ({association.acronym})"
        )

    def testSocialNetworkModel(self):
        social_network = SocialNetwork.objects.first()
        self.assertEqual(
            str(social_network), f"{social_network.type} : {social_network.location}"
        )

    def testInstitutionModel(self):
        institution = Institution.objects.first()
        self.assertEqual(
            str(institution), f"{institution.name} ({institution.acronym})"
        )

    def testInstitutionComponentModel(self):
        component = InstitutionComponent.objects.first()
        self.assertEqual(str(component), f"{component.name}")

    def testActivityFieldModel(self):
        activity_field = ActivityField.objects.first()
        self.assertEqual(str(activity_field), f"{activity_field.name}")
