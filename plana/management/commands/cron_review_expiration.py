import datetime

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.management.base import BaseCommand
from django.utils.translation import gettext as _

from plana.apps.associations.models.association import Association
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.project import Project
from plana.apps.users.models.user import AssociationUser, User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class Command(BaseCommand):
    help = _(
        "If a project that earned financial support from a commission didn't submit a review one month after its planned end date, send an email."
    )

    def handle(self, *args, **options):
        try:
            today = datetime.date.today()
            mail_sending_due_date = today - datetime.timedelta(days=settings.CRON_DAYS_BEFORE_REVIEW_EXPIRATION)
            projects_needing_reviews = Project.visible_objects.filter(
                project_status__in=Project.ProjectStatus.get_review_needed_project_statuses(),
                planned_end_date__year=mail_sending_due_date.year,
                planned_end_date__month=mail_sending_due_date.month,
                planned_end_date__day=mail_sending_due_date.day,
            )

            current_site = get_current_site(None)
            context = {"site_name": current_site.name}

            for project_needing_review in projects_needing_reviews:
                context["project_name"] = project_needing_review.name
                if project_needing_review.association_id is not None:
                    association = Association.objects.get(id=project_needing_review.association_id)
                    if project_needing_review.association_user_id is not None:
                        email = User.objects.get(
                            id=AssociationUser.objects.get(id=project_needing_review.association_user_id).user_id
                        ).email
                    else:
                        email = association.email
                    template = MailTemplate.objects.get(code="USER_OR_ASSOCIATION_PROJECT_NEEDS_REVIEW_SCHEDULED")
                    send_mail(
                        from_=settings.DEFAULT_FROM_EMAIL,
                        to_=email,
                        subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                        message=template.parse_vars(None, None, context),
                    )

                    managers_emails = list(
                        Institution.objects.get(id=association.institution_id)
                        .default_institution_managers()
                        .values_list("email", flat=True)
                    )
                    template = MailTemplate.objects.get(code="MANAGER_PROJECT_NEEDS_REVIEW_SCHEDULED")
                    send_mail(
                        from_=settings.DEFAULT_FROM_EMAIL,
                        to_=managers_emails,
                        subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                        message=template.parse_vars(None, None, context),
                    )

                elif project_needing_review.user_id is not None:
                    user = User.objects.get(id=project_needing_review.user_id)
                    template = MailTemplate.objects.get(code="USER_OR_ASSOCIATION_PROJECT_NEEDS_REVIEW_SCHEDULED")
                    send_mail(
                        from_=settings.DEFAULT_FROM_EMAIL,
                        to_=user.email,
                        subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                        message=template.parse_vars(None, None, context),
                    )

                    managers_emails = []
                    for user_to_check in User.objects.filter(is_superuser=False, is_staff=True):
                        if user_to_check.has_perm("users.change_user_misc"):
                            managers_emails.append(user_to_check.email)
                    template = MailTemplate.objects.get(code="MANAGER_PROJECT_NEEDS_REVIEW_SCHEDULED")
                    send_mail(
                        from_=settings.DEFAULT_FROM_EMAIL,
                        to_=managers_emails,
                        subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                        message=template.parse_vars(None, None, context),
                    )

        except Exception as error:
            self.stdout.write(self.style.ERROR(f"Error : {error}"))
