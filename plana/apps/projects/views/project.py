"""Views directly linked to projects."""
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.utils.datastructures import MultiValueDictKeyError
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.projects.models.project import Project
from plana.apps.projects.serializers.project import (
    ProjectPartialDataSerializer,
    ProjectRestrictedSerializer,
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
            and (
                not request.user.can_submit_projects
                or int(request.data["user"]) != request.user.pk
            )
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


@extend_schema(methods=["PUT"], exclude=True)
class ProjectRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """
    GET : Get a Project with all its details.

    PATCH : Update Project details.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

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

    def patch(self, request, *args, **kwargs):
        try:
            project = self.queryset.get(pk=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project not found.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        authorized_status = ["PROJECT_DRAFT", "PROJECT_PROCESSING"]
        if "status" in request.data and request.data["status"] not in authorized_status:
            return response.Response(
                {"error": _("Wrong status.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not project.can_edit_project(request.user):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        request.data["edition_date"] = datetime.now()
        return super().partial_update(request, *args, **kwargs)


@extend_schema(methods=["PUT"], exclude=True)
class ProjectRestrictedUpdate(generics.UpdateAPIView):
    """
    PATCH : Update Project restricted details.
    """

    queryset = Project.objects.all()
    serializer_class = ProjectRestrictedSerializer
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    # TODO : unittests
    # TODO : add institution notion to update restricted fields
    def patch(self, request, *args, **kwargs):
        try:
            project = self.queryset.get(pk=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project not found.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        if request.user.has_perm("projects.change_project_restricted_fields"):
            request.data["edition_date"] = datetime.now()
            return super().update(request, *args, **kwargs)
        else:
            return response.Response(
                {
                    "error": _(
                        "Not allowed to update restricted fields for this project."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )
