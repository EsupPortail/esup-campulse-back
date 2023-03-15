"""Views directly linked to projects."""
from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.projects.models.project import Project
from plana.apps.projects.serializers.project import ProjectSerializer


class ProjectRetrieve(generics.RetrieveAPIView):
    """
    GET : Get a Project with all its details.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            project_id = kwargs["pk"]
            project = self.queryset.get(id=project_id)
        except (ObjectDoesNotExist, MultiValueDictKeyError):
            return response.Response(
                {"error": _("No project found for this ID.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        return self.retrieve(request, *args, **kwargs)
