import os
import pathlib

from django.contrib.auth.models import Group, Permission
from django.core.management import call_command
from django.core.management.base import BaseCommand

from plana.settings.permissions import PERMISSIONS_GROUPS


class Command(BaseCommand):
    help = (
        "Applies permissions to groups according to the settings/permissions.py file."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            help="Set without value if database should be flushed before.",
            action="store_true",
        )

    def handle(self, *args, **options):
        try:
            if options["flush"] == True:
                call_command('flush')
                os.remove('plana/apps/groups/fixtures/auth_permission.json')
                os.remove('plana/apps/groups/fixtures/auth_group_permissions.json')
                apps_fixtures = list(
                    pathlib.Path().glob('plana/apps/*/fixtures/*.json')
                )
                call_command('loaddata', *apps_fixtures)
                libs_fixtures = list(
                    pathlib.Path().glob('plana/libs/*/fixtures/*.json')
                )
                call_command('loaddata', *libs_fixtures)

            for group in Group.objects.all():
                group.permissions.clear()
                for new_group_permission in PERMISSIONS_GROUPS[group.name]:
                    group.permissions.add(
                        Permission.objects.get(codename=new_group_permission)
                    )
            call_command(
                'dumpdata',
                'auth.permission',
                indent=2,
                output='plana/apps/groups/fixtures/auth_permission.json',
            )
            call_command(
                'dumpdata',
                'auth.group_permissions',
                indent=2,
                output='plana/apps/groups/fixtures/auth_group_permissions.json',
            )
            self.stdout.write(self.style.SUCCESS("Updated all group permissions."))

        except Exception as e:
            self.stdout.write(self.style.ERROR("Error : %s" % e))
