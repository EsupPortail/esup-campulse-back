"""Models describing projects."""
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.validators import MinValueValidator
from django.db import models
from django.db.models import Sum, Count, Q
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.commissions.models.commission import Commission
from plana.apps.commissions.models.commission_fund import CommissionFund
from plana.apps.commissions.models.fund import Fund
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.managers.visible_project_manager import (
    VisibleProjectManager,
)
from plana.apps.projects.models.project_commission_fund import ProjectCommissionFund
from plana.apps.users.models.user import AssociationUser, User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class Project(models.Model):
    """Main model."""

    class ProjectStatus(models.TextChoices):
        """List of statuses a project can have (for itself or reviews)."""

        PROJECT_DRAFT = "PROJECT_DRAFT", _("Project Draft")
        PROJECT_DRAFT_PROCESSED = "PROJECT_DRAFT_PROCESSED", _("Project Draft Processed")
        PROJECT_PROCESSING = "PROJECT_PROCESSING", _("Project Processing")
        PROJECT_REJECTED = "PROJECT_REJECTED", _("Project Rejected")
        PROJECT_VALIDATED = "PROJECT_VALIDATED", _("Project Validated")
        PROJECT_REVIEW_DRAFT = "PROJECT_REVIEW_DRAFT", _("Project Review Draft")
        PROJECT_REVIEW_PROCESSING = "PROJECT_REVIEW_PROCESSING", _("Project Review Processing")
        PROJECT_REVIEW_VALIDATED = "PROJECT_REVIEW_VALIDATED", _("Project Review Validated")
        PROJECT_CANCELED = "PROJECT_CANCELED", _("Project Canceled")

        @staticmethod
        def get_project_statuses_order():
            """Status can only be changed to the next associated number."""
            return {
                "PROJECT_DRAFT": 1,
                "PROJECT_DRAFT_PROCESSED": 1,
                "PROJECT_PROCESSING": 2,
                "PROJECT_REJECTED": 3,
                "PROJECT_VALIDATED": 3,
                "PROJECT_CANCELED": 4,
                "PROJECT_REVIEW_DRAFT": 4,
                "PROJECT_REVIEW_PROCESSING": 5,
                "PROJECT_REVIEW_VALIDATED": 6,
            }

        @staticmethod
        def get_rollbackable_project_statuses():
            """Statuses for projects that can be changed to the previous associated number."""
            return ["PROJECT_PROCESSING", "PROJECT_REVIEW_PROCESSING"]

        @staticmethod
        def get_unfinished_project_statuses():
            """Commission dates with projects having these statuses can be deleted."""
            return ["PROJECT_DRAFT", "PROJECT_DRAFT_PROCESSED"]

        @staticmethod
        def get_commentable_project_statuses():
            """Statuses for projects where managing comments is allowed."""
            return [
                "PROJECT_DRAFT",
                "PROJECT_DRAFT_PROCESSED",
                "PROJECT_PROCESSING",
                "PROJECT_VALIDATED",
                "PROJECT_REVIEW_DRAFT",
                "PROJECT_REVIEW_PROCESSING",
            ]

        @staticmethod
        def get_identifier_project_statuses():
            """If project has one of these statuses, create manual identifier for it."""
            return ["PROJECT_PROCESSING"]

        @staticmethod
        def get_email_project_processing_project_statuses():
            """If project has one of these statuses, send an email to warn managers."""
            return ["PROJECT_PROCESSING"]

        @staticmethod
        def get_validated_fund_project_statuses():
            """If funds are validated for a project with these statuses, validate the project."""
            return ["PROJECT_PROCESSING"]

        @staticmethod
        def get_commissionnable_project_statuses():
            """Projects with those statuses are validated but without a review."""
            return [
                "PROJECT_VALIDATED",
                "PROJECT_REVIEW_DRAFT",
                "PROJECT_REVIEW_PROCESSING",
            ]

        @staticmethod
        def get_review_needed_project_statuses():
            """Projects with those statuses need to submit a review."""
            return ["PROJECT_REVIEW_DRAFT"]

        @staticmethod
        def get_email_review_processing_project_statuses():
            """If project has one of these statuses, send an email to warn managers."""
            return ["PROJECT_REVIEW_PROCESSING"]

        @staticmethod
        def get_archived_project_statuses():
            """Statuses for projects that can't be updated anymore."""
            return [
                "PROJECT_REJECTED",
                "PROJECT_REVIEW_VALIDATED",
                "PROJECT_CANCELED",
            ]

        @staticmethod
        def get_bearer_project_statuses():
            """Statuses for projects that can be set by project bearer."""
            return ["PROJECT_PROCESSING", "PROJECT_REVIEW_PROCESSING"]

        @staticmethod
        def get_validator_project_statuses():
            """Statuses for projects that can be set by project validator."""
            return [
                "PROJECT_DRAFT",
                "PROJECT_DRAFT_PROCESSED",
                "PROJECT_REJECTED",
                "PROJECT_VALIDATED",
                "PROJECT_REVIEW_DRAFT",
                "PROJECT_REVIEW_VALIDATED",
                "PROJECT_CANCELED",
            ]

    name = models.CharField(_("Name"), max_length=100, blank=False)
    manual_identifier = models.CharField(_("Manual identifier"), max_length=8, unique=True, null=True)
    planned_start_date = models.DateTimeField(_("Planned start date"), null=True)
    planned_end_date = models.DateTimeField(_("Planned end date"), null=True)
    planned_location = models.TextField(_("Planned location"), default="")
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE, null=True)
    association = models.ForeignKey(Association, verbose_name=_("Association"), on_delete=models.CASCADE, null=True)
    association_user = models.ForeignKey(
        AssociationUser,
        verbose_name=_("Association User"),
        on_delete=models.SET_NULL,
        null=True,
    )
    partner_association = models.TextField(_("Partner association"), default="")
    budget_previous_edition = models.PositiveIntegerField(_("Budget on previous edition"), default=1)
    target_audience = models.TextField(_("Target audience"), default="")
    amount_students_audience = models.PositiveIntegerField(_("Amount of students in target audience"), default=0)
    amount_all_audience = models.PositiveIntegerField(
        _("Amount of all people in target audience"), default=1, validators=[MinValueValidator(1)]
    )
    ticket_price = models.PositiveIntegerField(_("Amount of money asked for each person"), default=0)
    student_ticket_price = models.PositiveIntegerField(_("Amount of money asked for a student"), default=0)
    individual_cost = models.PositiveIntegerField(
        _("Amount of money needed by person"), default=1, validators=[MinValueValidator(1)]
    )
    goals = models.TextField(_("Goals"), default="")
    summary = models.TextField(_("Summary"), default="")
    planned_activities = models.TextField(_("Planned activites"), default="")
    prevention_safety = models.TextField(_("Planned prevention and safety actions"), default="")
    marketing_campaign = models.TextField(_("Marketing campaign"), default="")
    sustainable_development = models.TextField(_("Sustainable development"), default="")
    project_status = models.CharField(
        _("Project Status"),
        max_length=32,
        choices=ProjectStatus.choices,
        default="PROJECT_DRAFT",
    )
    creation_date = models.DateTimeField(_("Creation date"), auto_now_add=True)
    edition_date = models.DateTimeField(_("Edition date"), auto_now=True)
    processing_date = models.DateTimeField(_("Processing date"), null=True)
    outcome = models.PositiveIntegerField(_("Outcome"), default=0)
    income = models.PositiveIntegerField(_("Income"), default=0)
    real_start_date = models.DateTimeField(_("Real start date"), null=True)
    real_end_date = models.DateTimeField(_("Real end date"), null=True)
    real_location = models.TextField(_("Real location"), default="")
    review = models.TextField(_("Review (amount of students, partnerships, ...)"), default="")
    impact_students = models.TextField(_("Impact on students"), default="")
    description = models.TextField(_("Description (activities done, changes from planning, ...)"), default="")
    difficulties = models.TextField(_("Difficulties"), default="")
    improvements = models.TextField(_("Improvements"), default="")
    categories = models.ManyToManyField("Category", through="ProjectCategory")

    objects = models.Manager()
    visible_objects = VisibleProjectManager()

    def get_project_default_manager_emails(self, fund_id=None):
        """Return a list of manager email addresses affected to a project."""
        managers_emails = []
        if fund_id:
            project_commission_funds = ProjectCommissionFund.objects.filter(
                project_id=self.id,
                commission_fund_id__in=CommissionFund.objects.filter(
                    fund_id=Fund.objects.get(id=fund_id).id
                ).values_list("id"),
            )
            if project_commission_funds.exists():
                managers_emails = list(
                    Institution.objects.get(id=Fund.objects.get(id=fund_id).institution_id)
                    .default_institution_managers()
                    .values_list("email", flat=True)
                )
        else:
            misc_project_commission_funds = ProjectCommissionFund.objects.filter(
                project_id=self.id,
                commission_fund_id__in=CommissionFund.objects.filter(
                    fund_id__in=Fund.objects.filter(is_site=False).values_list("id")
                ).values_list("id"),
            )
            if self.association_id :
                managers_emails = list(
                    Institution.objects.get(id=Association.objects.get(id=self.association_id).institution_id)
                    .default_institution_managers()
                    .values_list("email", flat=True)
                )
            if self.user_id or misc_project_commission_funds.exists():
                managers_emails.extend(
                    User.objects
                    .filter(
                        is_superuser=False,
                        is_staff=True,
                        # Check the permission "users.change_user_misc"
                        groupinstitutionfunduser__group__permissions__content_type__app_label='users',
                        groupinstitutionfunduser__group__permissions__codename='change_user_misc')
                    .values_list('email', flat=True)
                )
        return managers_emails

    def get_project_owner_data(self) -> dict:
        if self.association:
            owner = self.association
            return {
                "name": owner.name,
                "address": f"{owner.address} {owner.city} - {owner.zipcode}, {owner.country}",
                "email": self.association_user.user.email if self.association_user else owner.email
            }
        elif self.user:
            owner = self.user
            return {
                "name": f"{owner.first_name} {owner.last_name}",
                "address": f"{owner.address} {owner.city} - {owner.zipcode}, {owner.country}",
                "email": self.user.email
            }
        return {}

    @property
    def commissions(self):
        return Commission.objects.filter(
            commissionfund__projectcommissionfund__project=self
        ).distinct()

    def can_transition_to_status(self, new_status: str) -> bool:
        """
        Checks if the new status is near the actual one in priority order
        Cannot change status if the current one is already a finished status
        Can roll back status with a delta of 1 if current status is authorized to rollback
        Else accept delta of one to move forward in priority order
        """
        if self.project_status in self.ProjectStatus.get_archived_project_statuses():
            return False

        statuses_order = self.ProjectStatus.get_project_statuses_order()
        current_order = statuses_order.get(self.project_status, 0)
        new_order = statuses_order.get(new_status, 0)

        delta = new_order - current_order
        if delta == 1:
            return True
        if delta == -1 and self.project_status in self.ProjectStatus.get_rollbackable_project_statuses():
            return True

        return False

    def process_project_pcf_amount_earned_status_update(self) -> None:
        """
        Checks if every pcf amount_earned has been defined, and update project status accordingly if so
        A project is considered finished one way (waiting review) or another (canceled) when all pcf amount_earned have been set up
        """
        stats = self.projectcommissionfund_set.aggregate(
            has_pending_amount_count=Count("id", Q(amount_earned__isnull=True, is_validated_by_admin=True)),
            total_earned=Sum("amount_earned", default=0),
        )
        if stats["has_pending_amount_count"] == 0:
            new_status = self.ProjectStatus.PROJECT_REVIEW_DRAFT if stats["total_earned"] > 0 else self.ProjectStatus.PROJECT_CANCELED
            if self.project_status != new_status and self.can_transition_to_status(new_status):
                self.project_status = new_status
                self.save(update_fields=["project_status"])

    def process_project_pcf_admin_validation_status_update(self, request) -> None:
        """
        Checks if every pcf is_validated_by_admin has been defined, and update project status accordingly if so
        A project is considered ready for commission (validated) or not (rejected) when all pcf is_validated_by_admin have been set up
        """
        stats = self.projectcommissionfund_set.aggregate(
            unchecked_admin_count=Count("id", filter=Q(is_validated_by_admin__isnull=True)),
            validated_admin_count=Count("id", filter=Q(is_validated_by_admin=True)),
        )

        # There's still pcf waiting for first validation, do nothing here
        if stats["unchecked_admin_count"] > 0:
            return

        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
            "project_name": self.name,
        }
        owner_data = self.get_project_owner_data()

        if stats["validated_admin_count"] > 0:
            new_status = self.ProjectStatus.PROJECT_VALIDATED
            mail_code = "USER_OR_ASSOCIATION_PROJECT_CONFIRMATION"
        else:
            new_status = self.ProjectStatus.PROJECT_REJECTED
            mail_code = "USER_OR_ASSOCIATION_PROJECT_REJECTION"
            context["manager_email_address"] = ",".join(self.get_project_default_manager_emails())

        if self.project_status != new_status and self.can_transition_to_status(new_status):
            self.project_status = new_status
            self.save(update_fields=["project_status"])

        template = MailTemplate.objects.get(code=mail_code)
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=owner_data.get("email"),
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(request.user, request, context),
        )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
        permissions = [
            (
                "add_project_association",
                "Can add a project as an association.",
            ),
            (
                "add_project_user",
                "Can add a project as a user.",
            ),
            (
                "change_project_as_bearer",
                "Can update project fields filled by bearer (student).",
            ),
            (
                "change_project_as_validator",
                "Can update project fields filled by validator (manager).",
            ),
            (
                "view_project_any_fund",
                "Can view all projects for a fund.",
            ),
            (
                "view_project_any_institution",
                "Can view all projects for an institution.",
            ),
            (
                "view_project_any_status",
                "Can view all projects without status limit.",
            ),
        ]
