"""Views linked to project categories links."""
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.serializers.project_category import ProjectCategorySerializer
from plana.apps.users.models.user import AssociationUsers


class ProjectCategoryDestroy(generics.DestroyAPIView):
    """
    DELETE : Removess a link between Project and Category.
    """

    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    permission_classes = [IsAuthenticated]

    # TODO : update project edition_date ?
    def delete(self, request, *args, **kwargs):
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

        try:
            project_category = ProjectCategory.objects.get(
                project_id=kwargs["project_id"], category_id=kwargs["category_id"]
            )
        except ObjectDoesNotExist:
            return response.Response(
                status=status.HTTP_200_OK,
            )

        project_category.delete()
        return response.Response(
            status=status.HTTP_204_NO_CONTENT,
        )
