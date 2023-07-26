"""Views directly linked to commission exports."""
import csv

from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.associations.models import Association
from plana.apps.commissions.models import CommissionFund, Fund
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models import (
    Category,
    Project,
    ProjectCategory,
    ProjectCommissionFund,
)
from plana.apps.projects.serializers.project import ProjectSerializer
from plana.apps.users.models import User


class CommissionCSVExport(generics.RetrieveAPIView):
    """/commissions/{id}/csv_export route"""

    permission_classes = [IsAuthenticated]
    queryset = Project.visible_objects.all()
    serializer_class = ProjectSerializer

    @extend_schema(
        responses={
            status.HTTP_200_OK: ProjectSerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Projects presented to the commission CSV export."""

        queryset = self.get_queryset()
        commission_id = kwargs["pk"]

        try:
            self.queryset.get(id=kwargs["pk"])
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Commission does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        if not request.user.has_perm("projects.view_project_any_fund"):
            managed_funds = request.user.get_user_managed_funds()
            if managed_funds.count() > 0:
                user_funds_ids = managed_funds
            else:
                user_funds_ids = request.user.get_user_funds()
        else:
            user_funds_ids = Fund.objects.all().values_list("id")

        if not request.user.has_perm("projects.view_project_any_institution"):
            user_institutions_ids = request.user.get_user_managed_institutions()
        else:
            user_institutions_ids = Institution.objects.all().values_list("id")

        if not request.user.has_perm(
            "projects.view_project_any_fund"
        ) or not request.user.has_perm("projects.view_project_any_institution"):
            user_associations_ids = request.user.get_user_associations()
            user_projects_ids = Project.visible_objects.filter(
                models.Q(user_id=request.user.pk)
                | models.Q(association_id__in=user_associations_ids)
            ).values_list("id")

            queryset = queryset.filter(
                models.Q(id__in=user_projects_ids)
                | models.Q(
                    id__in=(
                        ProjectCommissionFund.objects.filter(
                            commission_fund_id__in=CommissionFund.objects.filter(
                                fund_id__in=user_funds_ids
                            ).values_list("id")
                        ).values_list("project_id")
                    )
                )
                | models.Q(
                    association_id__in=Association.objects.filter(
                        institution_id__in=user_institutions_ids
                    ).values_list("id")
                )
            )

        fields = [
            _("Project ID"),
            _("Project name"),
            _("Manual identifier"),
            _("Association name"),
            _("Student misc name"),
            _("Project start date"),
            _("Project end date"),
            _("First edition"),
            _("Categories"),
        ]

        funds = Fund.objects.all().order_by("acronym")
        for fund in funds:
            acronym = fund.acronym
            fields.append(_("Amount asked ") + acronym)
            fields.append(_("Amount earned ") + acronym)

        projects = queryset.filter(
            id__in=ProjectCommissionFund.objects.filter(
                commission_fund_id__in=CommissionFund.objects.filter(
                    commission_id=commission_id
                ).values("id")
            )
        ).order_by("id")

        http_response = HttpResponse(content_type="application/csv")
        http_response[
            "Content-Disposition"
        ] = f"Content-Disposition: attachment; filename=commission_{commission_id}_export.csv"

        writer = csv.writer(http_response, delimiter=";")
        # Write column titles for the CSV file
        writer.writerow([field for field in fields])

        for project in projects:
            association = (
                None
                if project.association_id is None
                else Association.objects.get(id=project.association_id).name
            )

            if project.user_id is None:
                user = None
            else:
                user = User.objects.get(id=project.user_id)
                user = f"{user.last_name} {user.first_name}"

            categories = list(
                Category.objects.filter(
                    id__in=ProjectCategory.objects.filter(
                        project_id=project.id
                    ).values_list("category_id")
                ).values_list("name", flat=True)
            )
            categories = ', '.join(categories)

            project_commission_funds = ProjectCommissionFund.objects.filter(
                project_id=project.id
            )

            is_first_edition = _("Yes")
            for edition in project_commission_funds:
                if not edition.is_first_edition:
                    is_first_edition = _("No")
                    break

            fields = [
                project.id,
                project.name,
                project.manual_identifier,
                association,
                user,
                project.planned_start_date.date(),
                project.planned_end_date.date(),
                is_first_edition,
                categories,
            ]
            for fund in funds:
                try:
                    pcf = ProjectCommissionFund.objects.get(
                        project_id=project.id,
                        commission_fund_id=CommissionFund.objects.get(
                            commission_id=commission_id, fund_id=fund.id
                        ).id,
                    )
                    fields.append(pcf.amount_asked)
                    fields.append(pcf.amount_earned)
                except ObjectDoesNotExist:
                    fields.append(0)
                    fields.append(0)

            # Write CSV file content
            writer.writerow([field for field in fields])

        return http_response
