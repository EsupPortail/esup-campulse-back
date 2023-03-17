"""Views linked to project categories links."""
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.serializers.project_category import ProjectCategorySerializer


# TODO : add correct permissions
class ProjectCategoryDestroy(generics.DestroyAPIView):
    """
    DELETE : Removess a link between Project and Category.
    """

    queryset = ProjectCategory.objects.all()
    serializer_class = ProjectCategorySerializer
    permission_classes = [IsAuthenticated]
