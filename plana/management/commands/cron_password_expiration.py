import datetime
import secrets
import string

from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.sites.shortcuts import get_current_site
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail

User = get_user_model()


class Command(BaseCommand):
    help = _("Expired password policy.")

    def handle(self, *args, **options):
        try:
            today = datetime.date.today()
            queryset = User.objects.all()

            # Send emails to accounts with nearly expired password (not changed in 11 months)
            mail_sending_due_date = today - datetime.timedelta(
                days=settings.CRON_DAYS_BEFORE_PASSWORD_EXPIRATION_WARNING
            )
            mail_sending_queryset = queryset.filter(password_last_change_date=mail_sending_due_date)

            current_site = get_current_site(None)
            context = {"site_name": current_site.name}
            template = MailTemplate.objects.get(code="USER_ACCOUNT_PASSWORD_RESET_WARNING_SCHEDULED")
            for user in mail_sending_queryset:
                self.send_password_mail(user, context, template)

            # Invalidate expired passwords (not changed in 12 months)
            change_due_date = today - datetime.timedelta(days=settings.CRON_DAYS_BEFORE_PASSWORD_EXPIRATION)
            change_password_queryset = queryset.filter(password_last_change_date=change_due_date)

            template = MailTemplate.objects.get(code="USER_ACCOUNT_PASSWORD_RESET_SCHEDULED")
            for user in change_password_queryset:
                password = "".join(
                    secrets.choice(string.ascii_letters + string.digits)
                    for i in range(settings.DEFAULT_PASSWORD_LENGTH)
                )
                user.set_password(password)
                user.save()
                self.send_password_mail(user, context, template)

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))

    def send_password_mail(self, user, context, template):
        """Generic function to send an email."""
        context["first_name"] = user.first_name
        context["last_name"] = user.last_name

        uid = user_pk_to_url_str(user)
        token = default_token_generator.make_token(user)
        context[
            "password_reset_url"
        ] = f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_PASSWORD_RESET_PATH}?uid={uid}&token={token}"

        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=user.email,
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(user, None, context),
        )
