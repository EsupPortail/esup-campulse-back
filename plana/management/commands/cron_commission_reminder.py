import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.utils.translation import gettext as _

from plana.apps.commissions.models import Fund
from plana.apps.projects.models.project import Project
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class Command(BaseCommand):
    help = _("Reminder for students and fund members of the following day upcoming commission data.")

    def handle(self, *args, **options):
        try:
            tomorrow = timezone.localdate() + datetime.timedelta(days=1)

            template = MailTemplate.objects.get(code="USER_OR_ASSOCIATION_PROJECT_CONFIRMATION")
            mail_subject = f"Rappel : {template.subject}"
            current_site = get_current_site(None)
            context = {"site_domain": current_site.domain, "site_name": current_site.name}

            projects = Project.objects.filter(
                project_status=Project.ProjectStatus.PROJECT_VALIDATED,
                projectcommissionfund__commission_fund__commission__commission_date=tomorrow
            ).distinct()

            for project in projects:
                commission = project.commission
                funds = Fund.objects.filter(
                    commissionfund__projectcommissionfund__project_id=project.pk,
                    commissionfund__projectcommissionfund__is_validated_by_admin=True
                ).distinct().values_list("acronym", flat=True)

                context.update({
                    "project_name": project.name,
                    "fund_name": ", ".join(funds),
                    "commission_name": commission.name,
                    "commission_date": commission.commission_date,
                    "commission_scheduled_time": commission.scheduled_time,
                    "commission_location": f"{commission.building} - {commission.room} - {commission.address}"
                })
                send_mail(
                    from_=settings.DEFAULT_FROM_EMAIL,
                    to_=project.get_project_owner_data().get("email"),
                    bcc_=commission.get_fund_members_emails(),
                    subject=mail_subject.replace("{{ site_name }}", context["site_name"]),
                    message=template.parse_vars(None, None, context),
                )

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
