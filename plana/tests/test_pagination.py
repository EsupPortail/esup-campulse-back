"""TestCase for custom pagination class"""

from unittest.mock import Mock

from django.test import TestCase

from plana.pagination import BasePageNumberPagination


class BasePageNumberPaginationTestCase(TestCase):
    """TestCase for custom pagination class"""
    def setUp(self):
        self.paginator = BasePageNumberPagination()
        self.data_set = list(range(1, 100))

    def test_base_page_number_custom_pagination(self):
        request = Mock()
        request.query_params = {"page": 1}
        page = self.paginator.paginate_queryset(self.data_set, request)
        response = self.paginator.get_paginated_response(page)

        # Paginated request format
        self.assertIn("count", response.data)
        self.assertIn("total_pages", response.data)
        self.assertIn("current_page", response.data)
        self.assertIn("range", response.data)
        self.assertIsNotNone(response.data["next"])

        # Data related
        self.assertEqual(len(page), 10)
        self.assertEqual(page[0], 1)
        self.assertEqual(response.data["total_pages"], 10)
        self.assertEqual(response.data["current_page"], 1)
        self.assertEqual(response.data["range"]["start"], 1)
        self.assertEqual(response.data["range"]["end"], 10)
