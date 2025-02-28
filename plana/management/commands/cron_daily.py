"""Global CRON dedicated to daily actions."""

from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _


class Command(BaseCommand):
    help = _("Global CRON daily launched.")

    def handle(self, *args, **options):
        call_command("cron_account_expiration")
        call_command("cron_association_expiration")
        call_command("cron_commission_expiration")
        call_command("cron_document_expiration")
        call_command("cron_goa_expiration")
        call_command("cron_history_expiration")
        call_command("cron_password_expiration")
        call_command("cron_project_expiration")
        call_command("cron_review_expiration")
