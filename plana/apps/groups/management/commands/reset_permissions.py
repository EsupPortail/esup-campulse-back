from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from plana.settings.permissions import PERMISSIONS_GROUPS


class Command(BaseCommand):
    help = (
        'Applies permissions to groups according to the settings/permissions.py file.'
    )

    def handle(self, *args, **options):
        for group in Group.objects.all():
            group.permissions.clear()
            for new_group_permission in PERMISSIONS_GROUPS[group.name]:
                group.permissions.add(
                    Permission.objects.get(codename=new_group_permission)
                )
        self.stdout.write('Updated all group permissions.')
