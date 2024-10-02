import pathlib

from django.core.management import call_command, CommandError
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = _("Import application initial datas.")

    def add_arguments(self, parser):
        parser.set_defaults(traceback=settings.DEBUG)
        parser.add_argument(
            "--storages",
            help=_("Set without value if storages should be added."),
            action="store_true",
        )
        parser.add_argument(
            "--test",
            help=_("Set without value if testing data should be added."),
            action="store_true",
        )

    def handle(self, *args, **options):
        try:
            if options["test"] is True:
                apps_fixtures = list(pathlib.Path().glob("plana/apps/*/fixtures/*.json"))
                # TODO Find a way to import documentupload fixtures with real files correctly for test environments.
                for app_fixture in apps_fixtures:
                    if app_fixture.name.endswith("documents_documentupload.json"):
                        apps_fixtures.remove(app_fixture)
                call_command("loaddata", *apps_fixtures)
                libs_fixtures = list(pathlib.Path().glob("plana/libs/*/fixtures/*.json"))
                call_command("loaddata", *libs_fixtures)
            else:
                call_command(
                    "loaddata",
                    [
                        "associations_activityfield",
                        "commissions_fund",
                        "contents_content",
                        "contents_logo",
                        "contents_setting",
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

        except CommandError:
            raise
        except Exception as error:
            raise CommandError(error) from error
