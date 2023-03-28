"""Views directly linked to projects categories."""


from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.projects.models.category import Category
from plana.apps.projects.serializers.category import CategorySerializer


@extend_schema_view(get=extend_schema(tags=["projects/categories"]))
class CategoryList(generics.ListAPIView):
    """/projects/categories/names route"""

    permission_classes = [AllowAny]
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

    def get(self, request, *args, **kwargs):
        """Lists all categories that can be linked to a project."""
        return self.list(request, *args, **kwargs)
