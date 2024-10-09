import datetime

from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.apps.contents.models.setting import Setting
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.projects.models.project import Project


class Command(BaseCommand):
    help = _("Deletes all Projects older than the given amount of years.")

    def handle(self, *args, **options):
        try:
            projects = Project.objects.all()
            archived_projects_ids = []
            amount_years_before_project_deletion = Setting.get_setting("AMOUNT_YEARS_BEFORE_PROJECT_DELETION")
            for project in projects:
                if datetime.datetime.now(
                    datetime.timezone(datetime.timedelta(hours=0))
                ) > project.edition_date + datetime.timedelta(days=(365 * amount_years_before_project_deletion)):
                    archived_projects_ids.append(project.id)
            projects = projects.filter(id__in=archived_projects_ids)

            documents = DocumentUpload.objects.filter(project_id__in=projects.values_list("id"))
            for document in documents:
                document.path_file.delete()
            documents.delete()
            projects.delete()
        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
