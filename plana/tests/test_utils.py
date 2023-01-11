from django.test import TestCase

from plana.utils import str_to_bool


class PlanAUtilsTests(TestCase):
    """
    Testing utils file functions.
    """

    def test_str_to_bool(self):
        """
        String is correctly converted to boolean.
        """
        value = str_to_bool("true")
        self.assertTrue(value)
