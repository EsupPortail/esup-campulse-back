import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.apps.associations.models.association import Association
from plana.apps.institutions.models.institution import Institution
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class Command(BaseCommand):
    help = _("Checks last General Ordinary Assembly date of associations.")

    def handle(self, *args, **options):
        try:
            institutions = Institution.objects.all()
            associations_goa_list = dict.fromkeys(
                institutions.values_list("id", flat=True), []
            )
            for association in Association.objects.all():
                if association.last_goa_date is None or (
                    datetime.date.today().month == association.last_goa_date.month
                    and datetime.date.today().year != association.last_goa_date.year
                ):
                    associations_goa_list[association.institution_id].append(
                        f"{association.name} - {association.last_goa_date}<br/>"
                    )

            template = MailTemplate.objects.get(code="ASSOCIATION_GOA_EXPIRING")
            current_site = get_current_site(None)
            context = {"site_name": current_site.name}
            for institution in institutions:
                if len(associations_goa_list[institution.id]) > 0:
                    context["associations_goa_list"] = ''.join(
                        associations_goa_list[institution.id]
                    )
                    send_mail(
                        from_=settings.DEFAULT_FROM_EMAIL,
                        to_=institution.default_institution_managers(),
                        subject=template.subject.replace(
                            "{{ site_name }}", context["site_name"]
                        ),
                        message=template.parse_vars(None, None, context),
                    )

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
