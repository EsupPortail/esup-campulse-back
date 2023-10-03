from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = _("Import application initial datas.")

    def add_arguments(self, parser):
        parser.add_argument(
            "--storages",
            help=_("Set without value if storages should be added."),
            action="store_true",
        )

    def handle(self, *args, **options):
        try:
            call_command(
                "loaddata",
                [
                    "associations_activityfield",
                    "associations_association_real",
                    "commissions_fund",
                    "contents_content",
                    "contents_logo",
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

            if options["storages"] is True:
                call_command("loaddata_storages")

            self.stdout.write(self.style.SUCCESS(_("Initial datas import - done")))

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
