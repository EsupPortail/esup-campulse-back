import os
import pathlib

from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.settings.permissions import PERMISSIONS_GROUPS


class Command(BaseCommand):
    help = _(
        "Applies permissions to groups according to the settings/permissions.py file."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            help=_("Set without value if database should be flushed before."),
            action="store_true",
        )

    def handle(self, *args, **options):
        try:
            if options["flush"] is True:
                call_command("flush")
                permission_fixtures_files = [
                    "plana/apps/groups/fixtures/auth_permission.json",
                    "plana/apps/groups/fixtures/auth_group_permissions.json",
                ]
                for fixture_file in permission_fixtures_files:
                    if os.path.isfile(fixture_file):
                        os.remove(fixture_file)
                all_fixtures_files = [
                    "plana/apps/*/fixtures/*.json",
                    "plana/libs/*/fixtures/*.json",
                ]
                for fixture_file in all_fixtures_files:
                    fixtures = list(pathlib.Path().glob(fixture_file))
                    call_command("loaddata", *fixtures)

            for group in Group.objects.all():
                group.permissions.clear()
                for new_group_permission in PERMISSIONS_GROUPS[group.name]:
                    group.permissions.add(
                        Permission.objects.get(codename=new_group_permission)
                    )
            call_command(
                "dumpdata",
                "auth.permission",
                indent=2,
                output="plana/apps/groups/fixtures/auth_permission.json",
            )
            call_command(
                "dumpdata",
                "auth.group_permissions",
                indent=2,
                output="plana/apps/groups/fixtures/auth_group_permissions.json",
            )
            self.stdout.write(self.style.SUCCESS(_("Updated all group permissions.")))

        except Exception as e:
            self.stdout.write(self.style.ERROR("Error : %s" % e))
