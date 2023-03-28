"""Views directly linked to projects categories."""

from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.projects.models.category import Category
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.serializers.category import CategorySerializer
from plana.apps.projects.serializers.project_category import ProjectCategorySerializer


# TODO Optimize this route to split in one route for each entity.
@extend_schema_view(
    get=extend_schema(tags=["projects/categories"]),
    post=extend_schema(tags=["projects/categories"]),
)
class CategoryListProjectCategoryCreate(generics.ListCreateAPIView):
    """/projects/categories GET route"""

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_queryset(self):
        if self.request.method == "POST":
            return ProjectCategory.objects.all()
        else:
            return Category.objects.all().order_by("name")

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = ProjectCategorySerializer
        else:
            self.serializer_class = CategorySerializer
        return super().get_serializer_class()

    def get(self, request, *args, **kwargs):
        """Lists all categories that can be linked to a project."""
        return self.list(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """Creates a link between a category and a project."""
        try:
            project = Project.objects.get(pk=request.data["project"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project not found.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not project.can_edit_project(request.user):
            return response.Response(
                {"error": _("Not allowed to update categories for this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.edition_date = datetime.now()
        project.save()

        try:
            ProjectCategory.objects.get(
                project_id=request.data["project"], category_id=request.data["category"]
            )
        except ObjectDoesNotExist:
            return super().create(request, *args, **kwargs)

        return response.Response({}, status=status.HTTP_200_OK)


@extend_schema_view(
    delete=extend_schema(tags=["projects/categories"]),
)
class ProjectCategoriesDestroy(generics.DestroyAPIView):
    """/projects/{project_id}/categories/{category_id} route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer

    def delete(self, request, *args, **kwargs):
        """Destroys a link between project and category."""
        try:
            project = Project.objects.get(pk=kwargs["project_id"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project not found.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not project.can_edit_project(request.user):
            return response.Response(
                {"error": _("Not allowed to update categories for this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        project.edition_date = datetime.now()
        project.save()

        try:
            project_category = ProjectCategory.objects.get(
                project_id=kwargs["project_id"], category_id=kwargs["category_id"]
            )
        except ObjectDoesNotExist:
            return response.Response({}, status=status.HTTP_200_OK)

        project_category.delete()
        return response.Response({}, status=status.HTTP_204_NO_CONTENT)
