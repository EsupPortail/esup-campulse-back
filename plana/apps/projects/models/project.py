"""Models describing projects."""

from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.users.models.user import User


class Project(models.Model):
    """Main model."""

    name = models.CharField(_("Name"), max_length=250, blank=False)
    planned_start_date = models.DateTimeField(_("Start date"), null=True)
    planned_end_date = models.DateTimeField(_("End date"), null=True)
    location = models.TextField(_("Location"), default="")
    user = models.ForeignKey(
        User, verbose_name=_("User"), on_delete=models.CASCADE, null=True
    )
    association = models.ForeignKey(
        Association, verbose_name=_("Association"), on_delete=models.CASCADE, null=True
    )
    budget_previous_edition = models.IntegerField(
        _("Budget on previous edition"), default=0
    )
    target_audience = models.TextField(_("Target audience"), default="")
    type_target_audience = models.CharField(
        _("Type of people in target audience (student, employees, ...)"),
        default="",
        max_length=64,
    )
    amount_target_audience = models.IntegerField(
        _("Amount of people in target audience"), default=0
    )
    amount_students_target_audience = models.IntegerField(
        _("Amount of students in target audience"), default=0
    )
    ticket_price = models.IntegerField(
        _("Amount of money asked for each person"), default=0
    )
    individual_cost = models.IntegerField(
        _("Amount of money needed by person"), default=0
    )
    goals = models.TextField(_("Goals"), default="")
    summary = models.TextField(_("Summary"), default="")
    planned_activities = models.TextField(_("Planned activites"), default="")
    prevention_safety = models.TextField(
        _("Planned prevention and safety actions"), default=""
    )
    marketing_campaign = models.TextField(_("Marketing campaign"), default="")
    status = models.CharField(
        _("Status"),
        max_length=32,
        choices=[
            ("PROJECT_DRAFT", _("Project Draft")),
            ("PROJECT_REJECTED", _("Project Rejected")),
            ("PROJECT_PROCESSING", _("Project Processing")),
            ("PROJECT_VALIDATED", _("Project Validated")),
            ("PROJECT_REVIEW_DRAFT", _("Project Review Draft")),
            ("PROJECT_REVIEW_REJECTED", _("Project Review Rejected")),
            ("PROJECT_REVIEW_PROCESSING", _("Project Review Processing")),
            ("PROJECT_REVIEW_VALIDATED", _("Project Review Validated")),
        ],
        default="PROJECT_DRAFT",
    )
    creation_date = models.DateTimeField(_("Creation date"), auto_now_add=True)
    edition_date = models.DateTimeField(_("Edition date"), auto_now=True)
    outcome = models.IntegerField(_("Outcome"), default=0)
    income = models.IntegerField(_("Income"), default=0)
    real_start_date = models.DateTimeField(_("Start date"), null=True)
    real_end_date = models.DateTimeField(_("End date"), null=True)
    organizer_name = models.CharField(_("Organizer name"), max_length=256, default="")
    organizer_phone = models.CharField(_("Organizer phone"), max_length=32, default="")
    organizer_email = models.CharField(_("Organizer email"), max_length=256, default="")
    review = models.TextField(
        _("Review (amount of students, partnerships, ...)"), default=""
    )
    impact_students = models.TextField(_("Impact on students"), default="")
    description = models.TextField(
        _("Description (activities done, changes from planning, ...)"), default=""
    )
    difficulties = models.TextField(_("Difficulties"), default="")
    improvements = models.TextField(_("Improvements"), default="")

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Project")
        verbose_name_plural = _("Projects")
