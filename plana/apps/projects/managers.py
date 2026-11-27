"""Managers for Projects models"""
import datetime

from django.apps import apps
from django.db import models
from django.db.models import (
    Case,
    Count,
    DurationField,
    ExpressionWrapper,
    F,
    IntegerField,
    OuterRef,
    Q,
    Subquery,
    Value,
    When,
)
from django.db.models.functions import Coalesce, ExtractDay, Greatest
from django.utils import timezone


class ProjectQuerySet(models.QuerySet):

    def annotate_bearer_counts(self):
        """
        Annotate some bearer counts for each project :
        - bearer_overdue_review_count for all overdue review that the bearer must still submit for other projects
        """
        from plana.apps.projects.models import Project
        Setting = apps.get_model('contents', 'Setting')

        today = datetime.date.today()
        review_due_date = today - datetime.timedelta(days=Setting.get_setting("DAYS_BEFORE_REVIEW_OVERDUE"))
        bearer_overdue_subquery = (
            Project.objects.filter(
                Q(user=OuterRef("user")) | Q(association=OuterRef("association")),
                project_status=Project.ProjectStatus.PROJECT_REVIEW_DRAFT,
                planned_end_date__lte=review_due_date,
            )
            .values("user", "association")
            .annotate(total=Count("pk"))
            .values("total")
        )

        return self.annotate(
            bearer_overdue_review_count=Coalesce(
                Subquery(bearer_overdue_subquery, output_field=IntegerField()),
                Value(0),
                output_field=IntegerField()
            )
        )

    def annotate_projects_data(self):
        """
        Annotate some projects additionnal data for each project :
        - review_overdue_days indicating the number of overdue days of the project's review,
            0 if not in designated statuses or planned_end_date still in the past
        """
        from plana.apps.projects.models import Project
        Setting = apps.get_model('contents', 'Setting')

        today = timezone.localdate()
        review_due_date = today - datetime.timedelta(days=Setting.get_setting("DAYS_BEFORE_REVIEW_OVERDUE"))

        return self.annotate(
            # Only calculating if planned_end_date is in the past and for the designated project statuses
            review_overdue_days=Case(
                When(
                    project_status__in=[
                        Project.ProjectStatus.PROJECT_REVIEW_DRAFT,
                        Project.ProjectStatus.PROJECT_REVIEW_PROCESSING
                        # Soon new status PROJECT_REVIEW_PROCESSED here
                    ],
                    planned_end_date__lte=today,
                    # Count days between review_due_date and planned_end_date (use greatest to avoid negative values)
                    then=Greatest(
                        ExtractDay(
                            ExpressionWrapper(
                                Value(review_due_date) - F("planned_end_date"),
                                output_field=DurationField()
                            )
                        ),
                        Value(0, output_field=IntegerField()),
                    )
                ),
                default=Value(0),
                output_field=IntegerField()
            )
        )

    def order_by_project_statuses_manage(self):
        """
        Order a projects list by specific statuses priorities
        """
        from plana.apps.projects.models import Project
        status_order = [
            Project.ProjectStatus.PROJECT_PROCESSING,
            Project.ProjectStatus.PROJECT_DRAFT_PROCESSED,
            Project.ProjectStatus.PROJECT_VALIDATED,
            Project.ProjectStatus.PROJECT_REVIEW_PROCESSING,
            # (soon new status PROJECT_REVIEW_DRAFT_PROCESSED here)
            Project.ProjectStatus.PROJECT_REVIEW_DRAFT,
            Project.ProjectStatus.PROJECT_REVIEW_VALIDATED,
            Project.ProjectStatus.PROJECT_CANCELED,
            Project.ProjectStatus.PROJECT_REJECTED,

        ]
        whens = [
            When(project_status=status_value, then=Value(index))
            for index, status_value in enumerate(status_order)
        ]
        return self.annotate(
            status_priority=Case(
                *whens,
                default=Value(len(status_order)),
                output_field=IntegerField(),
            )
        ).order_by("status_priority", "manual_identifier")
