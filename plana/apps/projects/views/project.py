"""Views directly linked to projects."""
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.projects.models.project import Project
from plana.apps.projects.serializers.project import (
    ProjectPartialDataSerializer,
    ProjectSerializer,
)
from plana.apps.users.models.user import AssociationUsers


class ProjectListCreate(generics.ListCreateAPIView):
    """
    GET : Get all Project with all their details.

    POST : Creates a new Project.
    """

    queryset = Project.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = ProjectSerializer
        else:
            self.serializer_class = ProjectPartialDataSerializer
        return super().get_serializer_class()

    # TODO: add filters to get projects

    # TODO: add unittests and make some permissions adjustments
    def post(self, request, *args, **kwargs):
        if (
            "association" in request.data
            and request.data["association"] != None
            and request.data["association"] != ""
        ) and (
            "user" in request.data
            and request.data["user"] != None
            and request.data["user"] != ""
        ):
            return response.Response(
                {"error": _("A project can only have one affectation.")},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if (
            not "association" in request.data
            or request.data["association"] == None
            or request.data["association"] == ""
        ) and (
            not "user" in request.data
            or request.data["user"] == None
            or request.data["user"] == ""
        ):
            return response.Response(
                {"error": _("Missing affectation of the new project.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            "user" in request.data
            and request.data["user"] != None
            and request.data["user"] != ""
            and not request.user.can_submit_projects
        ):
            return response.Response(
                {"error": _("Not allowed to create a new project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "association" in request.data
            and request.data["association"] != None
            and request.data["association"] != ""
        ):
            try:
                association = Association.objects.get(pk=request.data["association"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Association does not exist.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            if association.can_submit_projects:
                try:
                    member = AssociationUsers.objects.get(
                        association_id=request.data["association"],
                        user_id=request.user.pk,
                    )
                    if not member.is_president and not member.can_be_president:
                        return response.Response(
                            {"error": _("Not allowed to create a new project.")},
                            status=status.HTTP_403_FORBIDDEN,
                        )
                except ObjectDoesNotExist:
                    return response.Response(
                        {"error": _("Not allowed to create a new project.")},
                        status=status.HTTP_403_FORBIDDEN,
                    )
            else:
                return response.Response(
                    {"error": _("Not allowed to create a new project.")},
                    status=status.HTTP_403_FORBIDDEN,
                )

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
