import datetime

from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.translation import gettext as _

from plana.apps.history.models.history import History


class Command(BaseCommand):
    help = _("Deletes all History old lines.")

    def handle(self, *args, **options):
        try:
            expired_history = History.objects.filter(
                creation_date__lt=(
                    timezone.make_aware(
                        datetime.datetime.now() - datetime.timedelta(days=settings.CRON_DAYS_BEFORE_HISTORY_EXPIRATION)
                    )
                )
            )
            expired_history.delete()

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
