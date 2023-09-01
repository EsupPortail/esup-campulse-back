"""Views for project PDF generation."""

from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import DjangoModelPermissions, IsAuthenticated

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models import CommissionFund
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.fund import Fund
from plana.apps.documents.models.document import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.projects.models.category import Category
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_category import ProjectCategory
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.projects.serializers.project import ProjectSerializer
from plana.apps.projects.serializers.project_review import ProjectReviewSerializer
from plana.apps.users.models.user import AssociationUser, User
from plana.utils import generate_pdf


class ProjectDataExport(generics.RetrieveAPIView):
    """/projects/{id}/pdf_export route"""

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
            project = self.queryset.get(id=kwargs["pk"])
            data = project.__dict__
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

        if data["association_id"] is not None:
            data["association"] = Association.objects.get(
                id=data["association_id"]
            ).name
            if data["association_user_id"] is not None:
                data["user"] = User.objects.get(
                    id=AssociationUser.objects.get(
                        id=data["association_user_id"]
                    ).user_id
                )

        if data["user_id"] is not None:
            data["user"] = User.objects.get(id=data["user_id"])

        data["categories"] = list(Category.objects.all().values("id", "name"))

        data["project_categories"] = list(
            ProjectCategory.objects.filter(project_id=data["id"]).values_list(
                "category_id", flat=True
            )
        )

        data["project_commission_funds"] = list(
            ProjectCommissionFund.objects.filter(project_id=data["id"]).values(
                "commission_fund_id",
                "is_first_edition",
                "amount_asked_previous_edition",
                "amount_earned_previous_edition",
                "amount_asked",
                "amount_earned",
            )
        )
        for pcf in data["project_commission_funds"]:
            pcf["commission_data"] = Commission.objects.get(
                id=CommissionFund.objects.get(
                    id=pcf["commission_fund_id"]
                ).commission_id
            ).__dict__
            pcf["fund_data"] = Fund.objects.get(
                id=CommissionFund.objects.get(id=pcf["commission_fund_id"]).fund_id
            ).__dict__

        data["commission_name"] = data["project_commission_funds"][0][
            "commission_data"
        ]["name"]
        data["commission_date"] = data["project_commission_funds"][0][
            "commission_data"
        ]["commission_date"]

        data["is_first_edition"] = True
        for edition in data["project_commission_funds"]:
            if not edition["is_first_edition"]:
                data["is_first_edition"] = False
                break

        data["documents"] = list(
            DocumentUpload.objects.filter(
                project_id=data["id"],
                document_id__in=Document.objects.filter(
                    process_type="DOCUMENT_PROJECT"
                ),
            ).values("name", "document__name")
        )

        return generate_pdf(
            data["name"], data, "project_summary", request.build_absolute_uri("/")
        )


class ProjectReviewDataExport(generics.RetrieveAPIView):
    """/projects/{id}/review/pdf_export route"""

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
            project = self.queryset.get(id=kwargs["pk"])
            data = project.__dict__
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

        if data["association_id"] is not None:
            data["association"] = Association.objects.get(
                id=data["association_id"]
            ).name
            if data["association_user_id"] is not None:
                data["user"] = User.objects.get(
                    id=AssociationUser.objects.get(
                        id=data["association_user_id"]
                    ).user_id
                )

        if data["user_id"] is not None:
            data["user"] = User.objects.get(id=data["user_id"])

        data["project_commission_funds"] = list(
            ProjectCommissionFund.objects.filter(project_id=data["id"]).values(
                "commission_fund_id",
                "is_first_edition",
                "amount_asked_previous_edition",
                "amount_earned_previous_edition",
                "amount_asked",
                "amount_earned",
            )
        )
        for pcf in data["project_commission_funds"]:
            pcf["commission_data"] = Commission.objects.get(
                id=CommissionFund.objects.get(
                    id=pcf["commission_fund_id"]
                ).commission_id
            ).__dict__
            pcf["fund_data"] = Fund.objects.get(
                id=CommissionFund.objects.get(id=pcf["commission_fund_id"]).fund_id
            ).__dict__

        data["commission"] = data["project_commission_funds"][0]["commission_data"][
            "name"
        ]

        data["is_first_edition"] = True
        for edition in data["project_commission_funds"]:
            if not edition["is_first_edition"]:
                data["is_first_edition"] = False
                break

        data["documents"] = list(
            DocumentUpload.objects.filter(
                project_id=data["id"],
                document_id__in=Document.objects.filter(
                    process_type="DOCUMENT_PROJECT_REVIEW"
                ),
            ).values("name", "document__name")
        )

        return generate_pdf(
            data["name"],
            data,
            "project_review_summary",
            request.build_absolute_uri('/'),
        )
