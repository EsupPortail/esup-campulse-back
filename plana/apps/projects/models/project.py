"""Models describing projects."""

from django.core.validators import MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.institutions.models.institution import Institution
from plana.apps.projects.models.managers.visible_project_manager import (
    VisibleProjectManager,
)
from plana.apps.users.models.user import AssociationUser, User


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
                "PROJECT_REVIEW_DRAFT": 4,
                "PROJECT_REVIEW_PROCESSING": 5,
                "PROJECT_REVIEW_VALIDATED": 6,
                "PROJECT_CANCELED": 6,
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

    name = models.CharField(_("Name"), max_length=250, blank=False)
    manual_identifier = models.CharField(_("Manual identifier"), max_length=8, unique=True, null=True)
    planned_start_date = models.DateTimeField(_("Planned start date"), null=True)
    planned_end_date = models.DateTimeField(_("Planned end date"), null=True)
    planned_location = models.TextField(_("Planned location"), default="")
    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE, null=True)
    association = models.ForeignKey(Association, verbose_name=_("Association"), on_delete=models.CASCADE, null=True)
    association_user = models.ForeignKey(
        AssociationUser,
        verbose_name=_("Association User"),
        on_delete=models.CASCADE,
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

    objects = models.Manager()
    visible_objects = VisibleProjectManager()

    def get_project_default_manager_emails(self):
        """Return a list of manager email addresses affected to a project."""
        managers_emails = []
        if self.association_id is not None:
            managers_emails = list(
                Institution.objects.get(id=Association.objects.get(id=self.association_id).institution_id)
                .default_institution_managers()
                .values_list("email", flat=True)
            )
        if self.user_id is not None:
            for user_to_check in User.objects.filter(is_superuser=False, is_staff=True):
                if user_to_check.has_perm("users.change_user_misc"):
                    managers_emails.append(user_to_check.email)
        return managers_emails

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
