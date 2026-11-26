"""Daily CRON command to archive commissions."""

from django.core.management.base import BaseCommand
from django.db.models import OuterRef, Exists
from django.utils import timezone
from django.utils.translation import gettext as _

from plana.apps.commissions.models.commission import Commission
from plana.apps.projects.models import ProjectCommissionFund
from plana.apps.projects.models.project import Project


class Command(BaseCommand):
    help = _(
        "Archives all past commissions with only finished projects, and past commissions without projects at all."
    )

    def handle(self, *args, **options):
        try:
            archived_projects_statuses = (Project.ProjectStatus.get_archived_project_statuses())
            past_commissions = Commission.objects.filter(commission_date__lt=timezone.localdate(), is_archived=False)

            # Retrieve commissions with at least one unfinished project
            has_unfinished_project = ProjectCommissionFund.objects.filter(
                commission_fund__commission=OuterRef("pk"),
                project__isnull=False,
            ).exclude(
                project__project_status__in=archived_projects_statuses
            )

            # Exclude those commissions from past commissions, they are not ready to be archived
            commissions_to_archive = past_commissions.annotate(
                has_unfinished=Exists(has_unfinished_project)
            ).filter(has_unfinished=False)

            commissions_to_archive.update(is_archived=True)

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
