"""Views directly linked to commission exports."""
import csv

from django.http import HttpResponse
from django.utils.translation import gettext_lazy as _
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.associations.models import Association
from plana.apps.commissions.models import Commission, CommissionFund, Fund
from plana.apps.projects.models import (
    Category,
    Project,
    ProjectCategory,
    ProjectCommissionFund,
)
from plana.apps.projects.serializers.project import ProjectSerializer
from plana.apps.users.models import User


class CommissionProjectsCSVExport(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request, *args, **kwargs):
        """Projects presented to the commission CSV export."""
        queryset = self.get_queryset()
        commission_id = kwargs["pk"]

        funds = Fund.objects.all()
        http_response = HttpResponse(content_type="application/csv")
        http_response[
            "Content-Disposition"
        ] = f"Content-Disposition: attachment; filename='commission_{commission_id}_export.csv'"

        writer = csv.writer(http_response)
        # Write column titles for the CSV file
        writer.writerow(
            [
                _("Project ID"),
                _("Association name"),
                _("Student misc name"),
                _("Commission date"),
                _("Start Date"),
                _("End Date"),
                _("Reedition"),
                _("Categories"),
            ]
        )
        # Add amount asked and earned for each fund

        projects = queryset.filter(
            id__in=ProjectCommissionFund.objects.filter(
                commission_fund_id__in=CommissionFund.objects.filter(
                    commission_id=commission_id
                ).values("id")
            )
        ).order_by("id")
        for project in projects:
            association = (
                None
                if project.association_id is None
                else Association.objects.get(id=project.association_id).name
            )
            user = (
                None
                if project.user_id is None
                else User.objects.get(id=project.user_id).username
            )
            commission = Commission.objects.get(id=commission_id).name
            categories = list(
                Category.objects.filter(
                    id__in=ProjectCategory.objects.filter(
                        project_id=project.id
                    ).values_list("category_id")
                ).values_list("name")
            )
            project_commission_funds = ProjectCommissionFund.objects.filter(
                project_id=project.id
            )
            is_first_edition = True
            for edition in project_commission_funds:
                if not edition.is_first_edition:
                    is_first_edition = False
                    break

            # Write CSV file content
            writer.writerow(
                [
                    project.id,
                    association,
                    user,
                    commission,
                    project.planned_start_date,
                    project.planned_end_date,
                    is_first_edition,
                    categories,
                ]
            )

        return http_response
