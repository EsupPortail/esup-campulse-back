"""Views for project PDF generation."""

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models import OuterRef, Subquery
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission import Fund
from plana.apps.commissions.models.commission_date import CommissionDate
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_date import ProjectCommissionDate
from plana.apps.projects.serializers.project import (
    ProjectReviewSerializer,
    ProjectSerializer,
)
from plana.apps.users.models.user import User
from plana.utils import generate_pdf


class ProjectDataExport(generics.RetrieveAPIView):
    """/projects/{id}/export route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Project.visible_objects.all()
    serializer_class = ProjectSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves a PDF file."""
        try:
            project = self.queryset.get(id=kwargs["id"])
            data = project.__dict__
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm("projects.view_project_any_commission")
            and not request.user.has_perm("projects.view_project_any_institution")
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if data["association_id"] is not None:
            data["association"] = Association.objects.get(
                id=data["association_id"]
            ).name

        if data["user_id"] is not None:
            user = User.objects.get(id=data["user_id"])
            data["other_first_name"] = user.first_name
            data["other_last_name"] = user.last_name
            data["other_email"] = user.email
            data["other_phone"] = user.phone

        data["project_commission_dates"] = list(
            ProjectCommissionDate.objects.filter(project_id=data["id"]).values(
                "commission_date_id",
                "is_first_edition",
                "amount_asked_previous_edition",
                "amount_earned_previous_edition",
                "amount_asked",
                "amount_earned",
            )
        )
        commission_infos = list(
            CommissionDate.objects.filter(
                pk__in=[
                    pcd["commission_date_id"]
                    for pcd in data["project_commission_dates"]
                ]
            )
            .annotate(
                commission_acronym=Subquery(
                    Fund.objects.filter(id=OuterRef("commission_id")).values("acronym"),
                    output_field=models.CharField(),
                )
            )
            .values("commission_acronym", "commission_date", "id")
        )
        for commission in commission_infos:
            for link in data["project_commission_dates"]:
                if commission["id"] == link["commission_date_id"]:
                    link["commission_acronym"] = commission["commission_acronym"]
                    link["commission_date"] = commission["commission_date"]

        data["is_first_edition"] = True
        for edition in data["project_commission_dates"]:
            if not edition["is_first_edition"]:
                data["is_first_edition"] = False
                break

        data["documents"] = list(
            DocumentUpload.objects.filter(project_id=data["id"]).values(
                "name", "document__name"
            )
        )

        # print(data)
        return generate_pdf(data, "project_summary", request.build_absolute_uri("/"))


class ProjectReviewDataExport(generics.RetrieveAPIView):
    """/projects/{id}/review/export route"""

    permission_classes = [IsAuthenticated, DjangoModelPermissions]
    queryset = Project.visible_objects.all()
    serializer_class = ProjectReviewSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves a PDF file."""
        try:
            project = self.queryset.get(id=kwargs["id"])
            data = project.__dict__
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Project does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if (
            not request.user.has_perm("projects.view_project_any_commission")
            and not request.user.has_perm("projects.view_project_any_institution")
            and not request.user.can_access_project(project)
        ):
            return response.Response(
                {"error": _("Not allowed to retrieve this project.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if data["association_id"] is not None:
            data["association"] = Association.objects.get(
                id=data["association_id"]
            ).name

        if data["user_id"] is not None:
            user = User.objects.get(id=data["user_id"])
            data["other_first_name"] = user.first_name
            data["other_last_name"] = user.last_name
            data["other_email"] = user.email
            data["other_phone"] = user.phone

        data["project_commission_dates"] = list(
            ProjectCommissionDate.objects.filter(project_id=data["id"]).values(
                "commission_date_id",
                "is_first_edition",
                "amount_asked_previous_edition",
                "amount_earned_previous_edition",
                "amount_asked",
                "amount_earned",
            )
        )
        commission_infos = list(
            CommissionDate.objects.filter(
                pk__in=[
                    pcd["commission_date_id"]
                    for pcd in data["project_commission_dates"]
                ]
            )
            .annotate(
                commission_acronym=Subquery(
                    Fund.objects.filter(id=OuterRef("commission_id")).values("acronym"),
                    output_field=models.CharField(),
                )
            )
            .values("commission_acronym", "commission_date", "id")
        )
        for commission in commission_infos:
            for link in data["project_commission_dates"]:
                if commission["id"] == link["commission_date_id"]:
                    link["commission_acronym"] = commission["commission_acronym"]
                    link["commission_date"] = commission["commission_date"]

        data["is_first_edition"] = True
        for edition in data["project_commission_dates"]:
            if not edition["is_first_edition"]:
                data["is_first_edition"] = False
                break

        data["documents"] = list(
            DocumentUpload.objects.filter(project_id=data["id"]).values(
                "name", "document__name"
            )
        )

        # print(data)
        return generate_pdf(
            data, "project_review_summary", request.build_absolute_uri('/')
        )
