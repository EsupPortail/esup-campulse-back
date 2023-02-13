from django.contrib.auth.models import Group, Permission
from django.core import management
from django.core.management.base import BaseCommand

from plana.settings.permissions import PERMISSIONS_GROUPS


class Command(BaseCommand):
    help = (
        "Applies permissions to groups according to the settings/permissions.py file."
    )

    def handle(self, *args, **options):
        try:
            for group in Group.objects.all():
                group.permissions.clear()
                for new_group_permission in PERMISSIONS_GROUPS[group.name]:
                    group.permissions.add(
                        Permission.objects.get(codename=new_group_permission)
                    )
            management.call_command(
                'dumpdata',
                'auth.permission',
                indent=2,
                output='plana/apps/groups/fixtures/auth_permission.json',
            )
            management.call_command(
                'dumpdata',
                'auth.group_permissions',
                indent=2,
                output='plana/apps/groups/fixtures/auth_group_permissions.json',
            )
            self.stdout.write(self.style.SUCCESS("Updated all group permissions."))

        except Exception as e:
            self.stdout.write(self.style.ERROR("Error : %s" % e))
