"""Views directly linked to project reviews."""
import datetime

from django.core.exceptions import ObjectDoesNotExist
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
    """/projects/{id}/review route"""

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

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
        """Retrieves a project review with all its details."""
        try:
            project = self.get_queryset().get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

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
        exclude=True,
        responses={
            status.HTTP_405_METHOD_NOT_ALLOWED: None,
        },
    )
    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

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
        """Updates project review details."""
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            project = self.get_queryset().get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

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
            and project.project_status != "PROJECT_REVIEW_DRAFT"
        ):
            return response.Response(
                {"error": _("Project review is not a draft that can be edited.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if (
            "real_start_date" in request.data
            and "real_end_date" in request.data
            and datetime.datetime.strptime(
                request.data["real_start_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
            > datetime.datetime.strptime(
                request.data["real_end_date"], "%Y-%m-%dT%H:%M:%S.%fZ"
            )
        ):
            return response.Response(
                {"error": _("Can't set start date after end date.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        pending_commission_dates_count = ProjectCommissionFund.objects.filter(
            project_id=kwargs["pk"],
            commission_fund_id__in=CommissionFund.objects.filter(
                commission_id__in=Commission.objects.filter(
                    commission_date__gt=datetime.datetime.now()
                ).values_list("id")
            ).values_list("id"),
        ).count()
        if pending_commission_dates_count > 0:
            return response.Response(
                {
                    "error": _(
                        "Cannot edit review if commission dates are still pending."
                    )
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        request.data["edition_date"] = datetime.date.today()
        return self.partial_update(request, *args, **kwargs)
