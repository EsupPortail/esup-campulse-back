"""Views directly linked to projects."""
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.projects.models.project import Project
from plana.apps.projects.serializers.project import ProjectSerializer


class ProjectListCreate(generics.ListCreateAPIView):
    """
    GET : Get all Project with all their details.

    POST : Creates a new Project.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    # TODO: add filters to get projects + add a lighter serializer with mandatory informations

    # TODO: add proper permissions
    def post(self, request, *args, **kwargs):
        #        if not request.user.has_perm("projects.add_project"):
        #            return response.Response(
        #                {"error": _("Not allowed to create a new project.")},
        #                status=status.HTTP_403_FORBIDDEN,
        #            )
        #        # Raise a Forbidden or enforce user_id to match request.user.pk ?
        #        elif not request.user.pk != request.data["user_id"]:
        #            return response.Response(
        #                {"error": _("Not allowed to create a new project.")},
        #                status=status.HTTP_403_FORBIDDEN,
        #            )
        #
        request.data["creation_date"] = datetime.now()
        request.data["edition_date"] = datetime.now()

        return super().create(request, *args, **kwargs)


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
