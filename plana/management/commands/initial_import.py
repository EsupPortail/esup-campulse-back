from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):

    help = 'Import Opaline initial datas'

    def handle(self, *args, **options):
        try:
            call_command(
                'loaddata',
                [
                    'associations_activityfield',
                    'consents_gdprconsent',
                    'auth_group',
                    'auth_group_permissions',
                    'auth_permission',
                    'institutions_institution',
                    'institutions_institutioncomponent',
                    'mailtemplates',
                    'mailtemplatevars',
                ],
            )

            self.stdout.write(self.style.SUCCESS('Initial datas import - done'))

        except Exception as e:
            self.stdout.write(self.style.ERROR('Error : %s' % e))
