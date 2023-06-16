"""Views directly linked to commission exports."""
import csv

from django.core.exceptions import ObjectDoesNotExist
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

        fields = [
            _("Project ID"),
            _("Association name"),
            _("Student misc name"),
            _("Project start date"),
            _("Project end date"),
            _("Reedition"),
            _("Categories"),
        ]

        funds = Fund.objects.all().order_by("acronym")
        for fund in funds:
            fields.append(_(f"Amount asked {fund.acronym}"))
            fields.append(_(f"Amount earned {fund.acronym}"))

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
        ] = f"Content-Disposition: attachment; filename='commission_{commission_id}_export.csv'"

        writer = csv.writer(http_response)
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

            is_first_edition = True
            for edition in project_commission_funds:
                if not edition.is_first_edition:
                    is_first_edition = False
                    break

            fields = [
                project.id,
                association,
                user,
                project.planned_start_date,
                project.planned_end_date,
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
