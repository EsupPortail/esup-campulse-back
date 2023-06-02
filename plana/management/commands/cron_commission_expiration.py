import datetime

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.apps.commissions.models.commission import Commission
from plana.apps.projects.models.project import Project
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund


class Command(BaseCommand):
    help = _(
        "Deletes all ProjectCommissionFunds between Projects with PROJECT_DRAFT status and Commissions with expired submission_date."
    )

    def handle(self, *args, **options):
        try:
            ProjectCommissionFund.objects.filter(
                project_id__in=Project.visible_objects.filter(
                    project_status="PROJECT_DRAFT"
                ),
                commission_fund_id__in=Commission.objects.filter(
                    submission_date__lte=datetime.date.today()
                ),
            ).delete()

        except Exception as e:
            self.stdout.write(self.style.ERROR("Error : %s" % e))
