from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = _("Import application initial datas.")

    def handle(self, *args, **options):
        try:
            call_command(
                "loaddata",
                [
                    "associations_activityfield",
                    "commissions_commission",
                    "commissions_fund",
                    "contents_content",
                    "django_site",
                    "documents_document",
                    "auth_group",
                    "auth_group_permissions",
                    "auth_permission",
                    "institutions_institution",
                    "institutions_institutioncomponent",
                    "projects_category",
                    "mailtemplates",
                    "mailtemplatevars",
                ],
            )

            self.stdout.write(self.style.SUCCESS(_("Initial datas import - done")))

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
