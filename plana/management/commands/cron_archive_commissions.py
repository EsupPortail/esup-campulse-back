"""Daily CRON command to archive commissions."""

from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from django.utils.translation import gettext as _

from plana.apps.commissions.models.commission import Commission
from plana.apps.projects.models.project import Project


class Command(BaseCommand):
    help = _(
        "Archives all past commissions with only finished projects, and past commissions without projects at all."
    )

    def handle(self, *args, **options):
        try:
            archived_projects_statuses = (Project.ProjectStatus.get_archived_project_statuses())
            past_commissions = Commission.objects.filter(commission_date__lt=timezone.localdate())

            past_commissions_to_archive = past_commissions.filter(
                Q(commissionfund__projectcommissionfund__project__project_status__in=archived_projects_statuses)
                | Q(commissionfund__projectcommissionfund__isnull=True)
            )

            past_commissions_to_archive.update(is_archived=True)

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
