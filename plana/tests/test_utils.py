"""Tests for generic functions."""
from django.test import TestCase

from plana.utils import to_bool


class PlanAUtilsTests(TestCase):
    """Testing utils file functions."""

    def test_to_bool(self):
        """String is correctly converted to boolean."""
        val_str = to_bool("false")
        self.assertFalse(val_str)

        val_bool = to_bool(True)
        self.assertTrue(val_bool)
