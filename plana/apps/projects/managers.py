"""Managers for Projects models"""
import datetime

from django.apps import apps
from django.db import models
from django.db.models import Count, Q, OuterRef, Subquery, IntegerField, Value, Case, When
from django.db.models.functions import Coalesce


class ProjectQuerySet(models.QuerySet):

    def annotate_bearer_counts(self):
        """
        Annotate some bearer counts for each project :
        - bearer_overdue_review_count for all overdue review that the bearer must still submit for other projects
        """
        from plana.apps.projects.models import Project
        Setting = apps.get_model('contents', 'Setting')

        today = datetime.date.today()
        review_due_date = today - datetime.timedelta(days=Setting.get_setting("CRON_DAYS_BEFORE_REVIEW_EXPIRATION"))
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
