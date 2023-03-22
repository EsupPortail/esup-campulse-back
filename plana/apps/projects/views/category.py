"""Views directly linked to projects categories."""
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.projects.models.category import Category
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.serializers.category import CategorySerializer
from plana.apps.projects.serializers.project_category import ProjectCategorySerializer
from plana.apps.users.models.user import AssociationUsers


class CategoryListCreate(generics.ListCreateAPIView):
    """
    GET : Lists all Categories.

    POST : Creates a new link between Project and Category.
    """

    def get_serializer_class(self):
        if self.request.method == 'POST':
            self.serializer_class = ProjectCategorySerializer
        else:
            self.serializer_class = CategorySerializer
        return super().get_serializer_class()

    def get_queryset(self):
        if self.request.method == 'POST':
            return ProjectCategory.objects.all()
        else:
            return Category.objects.all().order_by("name")
        return super().get_queryset()

    def get_permissions(self):
        if self.request.method == 'POST':
            self.permission_classes = [IsAuthenticated]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    # TODO : update project edition_date ?
    def post(self, request, *args, **kwargs):
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

        try:
            ProjectCategory.objects.get(
                project_id=request.data["project"], category_id=request.data["category"]
            )
        except ObjectDoesNotExist:
            return super().create(request, *args, **kwargs)

        return response.Response(
            status=status.HTTP_200_OK,
        )
