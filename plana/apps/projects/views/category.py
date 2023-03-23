"""Views linked to projects categories."""
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.projects.models.category import Category
from plana.apps.projects.serializers.category import CategorySerializer


class CategoryList(generics.ListAPIView):
    """Lists all Categories."""

    permission_classes = [AllowAny]
    serializer_class = CategorySerializer

    def get_queryset(self):
        """GET : Lists all categories."""
        return Category.objects.all().order_by("name")
