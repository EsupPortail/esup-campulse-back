from django.test import TestCase, Client

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association
from plana.apps.associations.models.institution import Institution
from plana.apps.associations.models.institution_component import InstitutionComponent
from plana.apps.associations.models.social_network import SocialNetwork


class AssociationsModelsTests(TestCase):
    fixtures = [
        "associations_activityfield.json",
        "associations_association.json",
        "associations_institution.json",
        "associations_institutioncomponent.json",
        "associations_socialnetwork.json",
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
