import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils.translation import gettext as _

from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail

User = get_user_model()


class Command(BaseCommand):
    help = _("Expired accounts policy.")

    def handle(self, *args, **options):
        try:
            today = datetime.date.today()

            # FIXME: comptes inactifs ?
            # Get all users which aren't managers.
            queryset = User.objects.filter(is_staff=False)

            # Send emails to nearly expired accounts (not connected since 11 months)
            mail_sending_due_date = today - datetime.timedelta(days=(365 - 31))
            mail_sending_queryset = queryset.filter(
                Q(last_login__isnull=True, date_joined__date=mail_sending_due_date)
                | Q(last_login__isnull=False, last_login__date=mail_sending_due_date)
            )

            template = MailTemplate.objects.get(code="ACCOUNT_EXPIRATION")
            current_site = get_current_site(None)
            context = {"site_name": current_site.name}
            for user in mail_sending_queryset:
                context["first_name"] = user.first_name
                context["last_name"] = user.last_name
                send_mail(
                    from_=settings.DEFAULT_FROM_EMAIL,
                    to_=user.email,
                    subject=template.subject.replace(
                        "{{ site_name }}", context["site_name"]
                    ),
                    message=template.parse_vars(user, None, context),
                )

            # Delete expired accounts (not connected since 1 year)
            deletion_due_date = today - datetime.timedelta(days=365)
            deletion_queryset = queryset.filter(
                Q(last_login__isnull=True, date_joined__date__lte=deletion_due_date)
                | Q(last_login__isnull=False, last_login__date__lte=deletion_due_date)
            )
            deletion_queryset.delete()

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
