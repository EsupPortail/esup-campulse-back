import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.apps.associations.models.association import Association
from plana.apps.contents.models.setting import Setting
from plana.apps.institutions.models.institution import Institution
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class Command(BaseCommand):
    help = _("Checks statuses of associations charters.")

    def handle(self, *args, **options):
        try:
            associations = Association.objects.all()
            for association in associations:
                if (
                    association.charter_date is not None
                    and datetime.date.today()
                    == association.charter_date
                    + datetime.timedelta(
                        days=Setting.objects.get(setting="CRON_DAYS_BEFORE_ASSOCIATION_EXPIRATION_WARNING").parameters[
                            "value"
                        ]
                    )
                ):
                    template = MailTemplate.objects.get(code="ASSOCIATION_CHARTER_EXPIRATION_WARNING_SCHEDULED")
                    current_site = get_current_site(None)
                    context = {
                        "site_name": current_site.name,
                        "manager_email_address": ','.join(
                            Institution.objects.get(id=association.institution_id)
                            .default_institution_managers()
                            .values_list("email", flat=True)
                        ),
                    }
                    send_mail(
                        from_=settings.DEFAULT_FROM_EMAIL,
                        to_=association.email,
                        subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                        message=template.parse_vars(None, None, context),
                    )
                elif (
                    association.charter_date is not None
                    and datetime.date.today()
                    == association.charter_date
                    + datetime.timedelta(
                        days=Setting.objects.get(setting="CRON_DAYS_BEFORE_ASSOCIATION_EXPIRATION").parameters["value"]
                    )
                ):
                    association.charter_status = "CHARTER_EXPIRED"
                    association.save()

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
