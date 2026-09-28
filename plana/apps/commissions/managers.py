"""Managers for Commission models"""
import datetime

from django.db import models
from django.contrib.postgres.aggregates import ArrayAgg
from django.db.models import Count, Q


class CommissionQuerySet(models.QuerySet):

    def allowing_project_postpone(self, project_id: int):
        """
        Retrieve all Commissions that can allow a Project to be postponed into.
        Rules for a Commission to be eligible :
        - Commission date is in the future (compared to today)
        - All funds linked to the Project are available for the Commission
        """
        from .models import Fund
        today = datetime.date.today()

        project_funds_list = list(
            Fund.objects.filter(commissionfund__projectcommissionfund__project_id=project_id)
            .values_list("commissionfund__fund_id", flat=True)
            .distinct()
        )
        # If project does not exist or didn't apply for a fund yet, cannot postpone it
        if not project_funds_list:
            return self.none()

        return (
            self.annotate(commission_funds_array=ArrayAgg("commissionfund__fund_id"))
            .filter(
                commission_funds_array__contains=project_funds_list,
                commission_date__gt=today
            )
            # Only one commission per project for now, should not appear as a choice to postpone into (already linked)
            .exclude(commissionfund__projectcommissionfund__project_id=project_id)
            .distinct()
        )

    def annotate_projects_counts(self):
        """
        Annotate some projects counts for each commission :
        - submitted_projects_count for all non-draft submitted projects (all statuses included even review ones)
        - processing_projects_count for all submitted projects waiting for manager approval
        - standby_projects_count for all submitted projects waiting for bearer updates
        """
        from plana.apps.projects.models import Project
        return (
            self.annotate(
                submitted_projects_count=Count(
                    "commissionfund__projectcommissionfund__project",
                    filter=~Q(
                        commissionfund__projectcommissionfund__project__project_status=Project.ProjectStatus.PROJECT_DRAFT),
                    distinct=True,
                ),
                processing_projects_count=Count(
                    "commissionfund__projectcommissionfund__project",
                    filter=Q(
                        commissionfund__projectcommissionfund__project__project_status=Project.ProjectStatus.PROJECT_PROCESSING),
                    distinct=True,
                ),
                standby_projects_count=Count(
                    "commissionfund__projectcommissionfund__project",
                    filter=Q(
                        commissionfund__projectcommissionfund__project__project_status=Project.ProjectStatus.PROJECT_DRAFT_PROCESSED),
                    distinct=True,
                ),
            )
        )
