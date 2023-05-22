import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.apps.projects.models.project import Project


class Command(BaseCommand):
    help = _("Deletes all Projects older than the given amount of years.")

    def handle(self, *args, **options):
        try:
            projects = Project.objects.all()
            archived_projects_ids = []
            for project in projects:
                if datetime.datetime.now(
                    datetime.timezone(datetime.timedelta(hours=0))
                ) > project.edition_date + datetime.timedelta(
                    days=(365 * int(settings.AMOUNT_YEARS_BEFORE_PROJECT_DELETION))
                ):
                    archived_projects_ids.append(project.id)
            projects = projects.filter(id__in=archived_projects_ids)
            projects.delete()
        except Exception as e:
            self.stdout.write(self.style.ERROR("Error : %s" % e))
