"""Models describing projects."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.projects.models.managers.visible_project_manager import (
    VisibleProjectManager,
)
from plana.apps.users.models.user import User


class Project(models.Model):
    """Main model."""

    class ProjectStatus(models.TextChoices):
        """List of statuses a project can have (for itself or reviews)."""

        PROJECT_DRAFT = "PROJECT_DRAFT", _("Project Draft")
        PROJECT_PROCESSING = "PROJECT_PROCESSING", _("Project Processing")
        PROJECT_REJECTED = "PROJECT_REJECTED", _("Project Rejected")
        PROJECT_VALIDATED = "PROJECT_VALIDATED", _("Project Validated")
        PROJECT_REVIEW_DRAFT = "PROJECT_REVIEW_DRAFT", _("Project Review Draft")
        PROJECT_REVIEW_PROCESSING = "PROJECT_REVIEW_PROCESSING", _(
            "Project Review Processing"
        )
        PROJECT_REVIEW_REJECTED = "PROJECT_REVIEW_REJECTED", _(
            "Project Review Rejected"
        )
        PROJECT_REVIEW_VALIDATED = "PROJECT_REVIEW_VALIDATED", _(
            "Project Review Validated"
        )

        @staticmethod
        def get_project_statuses_order():
            """Status can only be changed to the next associated number."""

            return {
                "PROJECT_DRAFT": 1,
                "PROJECT_PROCESSING": 2,
                "PROJECT_REJECTED": 3,
                "PROJECT_VALIDATED": 3,
                "PROJECT_REVIEW_DRAFT": 4,
                "PROJECT_REVIEW_PROCESSING": 5,
                "PROJECT_REVIEW_REJECTED": 6,
                "PROJECT_REVIEW_VALIDATED": 6,
            }

        @staticmethod
        def get_rollbackable_project_statuses():
            """Statuses for projects that can be changed to the previous associated number."""

            return ["PROJECT_PROCESSING", "PROJECT_REVIEW_PROCESSING"]

        @staticmethod
        def get_draft_project_statuses():
            """Commission dates with projects having these statuses can be deleted."""

            return ["PROJECT_DRAFT"]

        @staticmethod
        def get_manageable_project_statuses():
            """Statuses for projects that trigger a mail sending to a validator."""

            return ["PROJECT_PROCESSING", "PROJECT_REVIEW_PROCESSING"]

        @staticmethod
        def get_review_needed_project_statuses():
            """Projects with those statuses need to submit a review."""

            return ["PROJECT_VALIDATED", "PROJECT_REVIEW_DRAFT"]

        @staticmethod
        def get_archived_project_statuses():
            """Statuses for projects that can't be updated anymore."""

            return [
                "PROJECT_REJECTED",
                "PROJECT_REVIEW_REJECTED",
                "PROJECT_REVIEW_VALIDATED",
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
                "PROJECT_REJECTED",
                "PROJECT_VALIDATED",
                "PROJECT_REVIEW_DRAFT",
                "PROJECT_REVIEW_REJECTED",
                "PROJECT_REVIEW_VALIDATED",
            ]

    name = models.CharField(_("Name"), max_length=250, blank=False)
    planned_start_date = models.DateTimeField(_("Planned start date"), null=True)
    planned_end_date = models.DateTimeField(_("Planned end date"), null=True)
    planned_location = models.TextField(_("Planned location"), default="")
    other_first_name = models.CharField(
        _("Other first name"), max_length=150, default="", null=True
    )
    other_last_name = models.CharField(
        _("Other last name"), max_length=150, default="", null=True
    )
    other_email = models.EmailField(
        _("Other email"), max_length=150, default="", null=True
    )
    other_phone = models.CharField(
        _("Other phone"), max_length=32, default="", null=True
    )
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )
    association = models.ForeignKey(
        Association, verbose_name=_("Association"), on_delete=models.CASCADE, null=True
    )
    budget_previous_edition = models.PositiveIntegerField(
        _("Budget on previous edition"), default=0
    )
    target_audience = models.TextField(_("Target audience"), default="")
    amount_students_audience = models.PositiveIntegerField(
        _("Amount of students in target audience"), default=0
    )
    amount_all_audience = models.PositiveIntegerField(
        _("Amount of all people in target audience"), default=0
    )
    ticket_price = models.PositiveIntegerField(
        _("Amount of money asked for each person"), default=0
    )
    individual_cost = models.PositiveIntegerField(
        _("Amount of money needed by person"), default=0
    )
    goals = models.TextField(_("Goals"), default="")
    summary = models.TextField(_("Summary"), default="")
    planned_activities = models.TextField(_("Planned activites"), default="")
    prevention_safety = models.TextField(
        _("Planned prevention and safety actions"), default=""
    )
    marketing_campaign = models.TextField(_("Marketing campaign"), default="")
    project_status = models.CharField(
        _("Project Status"),
        max_length=32,
        choices=ProjectStatus.choices,
        default="PROJECT_DRAFT",
    )
    creation_date = models.DateTimeField(_("Creation date"), auto_now_add=True)
    edition_date = models.DateTimeField(_("Edition date"), auto_now=True)
    outcome = models.PositiveIntegerField(_("Outcome"), default=0)
    income = models.PositiveIntegerField(_("Income"), default=0)
    real_start_date = models.DateTimeField(_("Real start date"), null=True)
    real_end_date = models.DateTimeField(_("Real end date"), null=True)
    real_location = models.TextField(_("Real location"), default="")
    review = models.TextField(
        _("Review (amount of students, partnerships, ...)"), default=""
    )
    impact_students = models.TextField(_("Impact on students"), default="")
    description = models.TextField(
        _("Description (activities done, changes from planning, ...)"), default=""
    )
    difficulties = models.TextField(_("Difficulties"), default="")
    improvements = models.TextField(_("Improvements"), default="")

    objects = models.Manager()
    visible_objects = VisibleProjectManager()

    def __str__(self):
        return f"{self.name}"

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
                "view_project_any_commission",
                "Can view all projects for a commission.",
            ),
            (
                "view_project_any_institution",
                "Can view all projects for an institution.",
            ),
        ]
