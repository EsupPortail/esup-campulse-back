"""Main pagination classes"""

from rest_framework import pagination
from rest_framework.response import Response


class BasePageNumberPagination(pagination.PageNumberPagination):
    """
    Custom base pagination class.
    Adding the following data on response : total_pages, current_page and items range within total (start and end indexes)
    """
    page_size = 10
    max_page_size = 100
    page_size_query_param = "page_size"

    def get_paginated_response(self, data):
        """Custom pagination data format"""
        return Response({
            "count": self.page.paginator.count,
            "total_pages": self.page.paginator.num_pages,
            "current_page": self.page.number,
            "range": {
                'start': self.page.start_index(),
                'end': self.page.end_index(),
            },
            "next": self.get_next_link(),
            "previous": self.get_previous_link(),
            "results": data
        })
