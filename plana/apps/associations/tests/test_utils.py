from django.test import Client, TestCase
from plana.apps.associations.utils import normalize_association_name


class AssociationUtilsTests(TestCase):
    """Tests class for associations utils methods."""

    def test_normalize_association_names(self):
        result = normalize_association_name(" Ceci est Un têst avèc  ACCENts ")
        self.assertEqual(result, "ceciestuntestavecaccents")
