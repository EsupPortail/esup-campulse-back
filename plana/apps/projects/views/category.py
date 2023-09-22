"""Views directly linked to projects categories."""
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from plana.apps.projects.models.category import Category
from plana.apps.projects.serializers.category import CategorySerializer


class CategoryList(generics.ListAPIView):
    """/projects/categories/names route."""

    permission_classes = [AllowAny]
    queryset = Category.objects.all().order_by("name")
    serializer_class = CategorySerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: CategorySerializer,
        },
        tags=["projects/categories"],
    )
    def get(self, request, *args, **kwargs):
        """List all categories that can be linked to a project."""
        return self.list(request, *args, **kwargs)
