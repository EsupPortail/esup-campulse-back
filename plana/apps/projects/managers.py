"""Managers for Projects models"""
import datetime

from django.db import models
from django.db.models import Count, Q, OuterRef, Subquery, IntegerField, Value
from django.db.models.functions import Coalesce

from plana.apps.contents.models import Setting


class ProjectQuerySet(models.QuerySet):

    # TODO : unittests
    def annotate_bearer_counts(self):
        """
        Annotate some bearer counts for each project :
        - bearer_overdue_review_count for all overdue review that the bearer must still submit for other projects
        """
        from plana.apps.projects.models import Project
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
