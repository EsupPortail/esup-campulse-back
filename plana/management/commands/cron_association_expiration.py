import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.apps.associations.models.association import Association
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
                    == association.charter_date + datetime.timedelta(days=355)
                ):
                    template = MailTemplate.objects.get(
                        code="ASSOCIATION_CHARTER_NEARLY_EXPIRED"
                    )
                    current_site = get_current_site(None)
                    context = {"site_name": current_site.name}
                    send_mail(
                        from_=settings.DEFAULT_FROM_EMAIL,
                        # TODO What if mail is not set ?
                        to_=association.email,
                        subject=template.subject.replace(
                            "{{ site_name }}", context["site_name"]
                        ),
                        message=template.parse_vars(None, None, context),
                    )
                elif (
                    association.charter_date is not None
                    and datetime.date.today()
                    == association.charter_date + datetime.timedelta(days=365)
                ):
                    association.charter_status = "CHARTER_EXPIRED"
                    association.save()

        except Exception as e:
            self.stdout.write(self.style.ERROR("Error : %s" % e))
