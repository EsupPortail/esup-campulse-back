import datetime

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.apps.commissions.models import CommissionFund
from plana.apps.commissions.models.commission import Commission
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund


class Command(BaseCommand):
    help = _(
        "Deletes all ProjectCommissionFunds between Projects with PROJECT_DRAFT status and Commissions with expired submission_date."
    )

    def handle(self, *args, **options):
        try:
            expired_commissions = Commission.objects.filter(
                submission_date__lte=datetime.date.today()
            )
            expired_commissions.update(is_open_to_projects=False)

            ProjectCommissionFund.objects.filter(
                project_id__in=Project.visible_objects.filter(
                    project_status=Project.ProjectStatus.get_unfinished_project_statuses()
                ),
                commission_fund_id__in=CommissionFund.objects.filter(
                    commission_id__in=expired_commissions.values_list("id"),
                ),
            ).delete()

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
