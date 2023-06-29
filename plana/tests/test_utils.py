"""Tests for generic functions."""
from django.test import TestCase

from plana.utils import to_bool, valid_date_format


class PlanAUtilsTests(TestCase):
    """Testing utils file functions."""

    def test_to_bool(self):
        """String is correctly converted to boolean."""
        val_str = to_bool("false")
        self.assertFalse(val_str)

        val_bool = to_bool(True)
        self.assertTrue(val_bool)

        val_int = to_bool(5)
        self.assertEqual(val_int, None)

    def test_valid_date_format(self):
        """String is correctly converted to boolean."""
        date_valid = valid_date_format("2023-06-29")
        self.assertTrue(date_valid)

        date_wrong = valid_date_format("29-06-2023")
        self.assertFalse(date_wrong)
