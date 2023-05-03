import datetime

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.apps.commissions.models import CommissionDate
from plana.apps.projects.models import Project, ProjectCommissionDate


class Command(BaseCommand):
    help = _(
        'Deletes all ProjectCommissionDates between Projects with PROJECT_DRAFT status and CommissionDates with expired submission_date.'
    )

    def handle(self, *args, **options):
        try:
            ProjectCommissionDate.objects.filter(
                project_id__in=Project.objects.filter(project_status="PROJECT_DRAFT"),
                commission_date_id__in=CommissionDate.objects.filter(
                    submission_date__lte=datetime.date.today()
                ),
            ).delete()

        except Exception as e:
            self.stdout.write(self.style.ERROR("Error : %s" % e))