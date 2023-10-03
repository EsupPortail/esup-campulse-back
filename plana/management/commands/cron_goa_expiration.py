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
            associations_goa_list = {x: [] for x in institutions.values_list("id", flat=True)}
            for association in Association.objects.all():
                if association.last_goa_date is None or (
                    datetime.date.today().month == association.last_goa_date.month
                    and datetime.date.today().year != association.last_goa_date.year
                ):
                    associations_goa_list[association.institution_id].append(
                        f"{association.name} {association.last_goa_date if association.last_goa_date else ''}"
                    )

            template = MailTemplate.objects.get(code="MANAGER_ACCOUNT_ASSOCIATION_GOA_EXPIRATION_SCHEDULED")
            current_site = get_current_site(None)
            context = {"site_name": current_site.name}
            email_addresses_used = []
            for institution in institutions:
                if len(associations_goa_list[institution.id]) > 0:
                    context["associations_goa_list"] = "\n".join(associations_goa_list[institution.id])
                    email_addresses_to_use = [
                        x
                        for x in list(institution.default_institution_managers().values_list("email", flat=True))
                        if x not in email_addresses_used
                    ]
                    send_mail(
                        from_=settings.DEFAULT_FROM_EMAIL,
                        to_=email_addresses_to_use,
                        subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                        message=template.parse_vars(None, None, context),
                    )
                    email_addresses_used += email_addresses_to_use

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
