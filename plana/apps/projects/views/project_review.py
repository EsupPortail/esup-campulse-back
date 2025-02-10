"""Views directly linked to project reviews."""

import datetime

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.commissions.models import Commission, CommissionFund
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.projects.serializers.project_review import (
    ProjectReviewSerializer,
    ProjectReviewUpdateSerializer,
)


class ProjectReviewRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """/projects/{id}/review route."""
    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    http_method_names = ["get", "patch"]

    def get_queryset(self):
        return Project.visible_objects.all()

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            self.serializer_class = ProjectReviewUpdateSerializer
        else:
            self.serializer_class = ProjectReviewSerializer
        return super().get_serializer_class()

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectReviewSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a project review with all its details."""
        project = self.get_object()

        if (
            not request.user.has_perm("projects.view_project_any_fund")
            and not request.user.has_perm("projects.view_project_any_institution")
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectReviewUpdateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update project review details."""
        project = self.get_object()

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not request.user.has_perm("projects.change_project_as_bearer"):
            return response.Response(
                {"error": _("Not allowed to update bearer fields for this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if not request.user.can_edit_project(project):
            return response.Response(
                {"error": _("Not allowed to update this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            not request.user.has_perm("projects.change_project_as_validator")
            and project.project_status not in Project.ProjectStatus.get_review_needed_project_statuses()
        ):
            return response.Response(
                {"error": _("Project review is not a draft that can be edited.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "real_start_date" in request.data
            and "real_end_date" in request.data
            and datetime.datetime.strptime(request.data["real_start_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
            > datetime.datetime.strptime(request.data["real_end_date"], "%Y-%m-%dT%H:%M:%S.%fZ")
        ):
            return response.Response(
                {"error": _("Can't set start date after end date.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["edition_date"] = datetime.date.today()
        return self.partial_update(request, *args, **kwargs)
