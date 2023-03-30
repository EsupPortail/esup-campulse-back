"""Views directly linked to projects."""
import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.projects.models.project import Project
from plana.apps.projects.serializers.project import (
    ProjectPartialDataSerializer,
    ProjectRestrictedSerializer,
    ProjectSerializer,
)
from plana.apps.users.models.user import AssociationUser


class ProjectListCreate(generics.ListCreateAPIView):
    """/projects/ route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Project.objects.all()

    def get_serializer_class(self):
        if self.request.method == "POST":
            self.serializer_class = ProjectSerializer
        else:
            self.serializer_class = ProjectPartialDataSerializer
        return super().get_serializer_class()

    def get(self, request, *args, **kwargs):
        """Lists all projects linked to a user, or all projects with all their details (manager)."""
        if request.user.has_perm("projects.view_project_all"):
            serializer = self.get_serializer(self.queryset.all(), many=True)
            return response.Response(serializer.data)

        user_associations_ids = AssociationUser.objects.filter(
            user_id=request.user.pk
        ).values_list("association_id")
        serializer = self.get_serializer(
            self.queryset.filter(
                Q(user_id=request.user.pk) | Q(association_id__in=user_associations_ids)
            ),
            many=True,
        )
        return response.Response(serializer.data)

    def post(self, request, *args, **kwargs):
        """Creates a new project."""
        if (
            "association" in request.data
            and request.data["association"] is not None
            and request.data["association"] != ""
        ):
            try:
                association = Association.objects.get(pk=request.data["association"])
            except ObjectDoesNotExist:
                return response.Response(
                    {"error": _("Association does not exist.")},
                    status=status.HTTP_404_NOT_FOUND,
                )

            if association.can_submit_projects:
                try:
                    member = AssociationUser.objects.get(
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

        if (
            "user" in request.data
            and request.data["user"] is not None
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
            and request.data["association"] is not None
            and request.data["association"] != ""
        ) and (
            "user" in request.data
            and request.data["user"] is not None
            and request.data["user"] != ""
        ):
            return response.Response(
                {"error": _("A project can only have one affectation.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if (
            not "association" in request.data
            or request.data["association"] is None
            or request.data["association"] == ""
        ) and (
            not "user" in request.data
            or request.data["user"] is None
            or request.data["user"] == ""
        ):
            return response.Response(
                {"error": _("Missing affectation of the new project.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["creation_date"] = datetime.date.today()
        request.data["edition_date"] = datetime.date.today()

        return super().create(request, *args, **kwargs)


@extend_schema(methods=["PUT"], exclude=True)
class ProjectRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """/projects/{id} route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get(self, request, *args, **kwargs):
        """Retrieves a project with all its details."""
        try:
            project = self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("projects.view_project_all") and (
            (project.user is not None and request.user.pk != project.user)
            or (
                project.association is not None
                and request.user.is_in_association(project.association)
            )
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        """Updates project details."""
        try:
            project = self.queryset.get(pk=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("projects.change_project_basic_fields"):
            return response.Response(
                {"error": _("Not allowed to update basic fields for this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        authorized_status = ["PROJECT_DRAFT", "PROJECT_PROCESSING"]
        if (
            "project_status" in request.data
            and request.data["project_status"] not in authorized_status
        ):
            return response.Response(
                {"error": _("Wrong status.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["edition_date"] = datetime.date.today()
        return self.partial_update(request, *args, **kwargs)


@extend_schema(methods=["PUT"], exclude=True)
class ProjectRestrictedUpdate(generics.UpdateAPIView):
    """/projects/{id}/restricted route"""

    queryset = Project.objects.all()
    serializer_class = ProjectRestrictedSerializer

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def patch(self, request, *args, **kwargs):
        """Updates project restricted details (manager only)."""
        try:
            self.queryset.get(pk=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("projects.change_project_restricted_fields"):
            return response.Response(
                {
                    "error": _(
                        "Not allowed to update restricted fields for this project."
                    )
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        request.data["edition_date"] = datetime.date.today()
        return self.update(request, *args, **kwargs)
