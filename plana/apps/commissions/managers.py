"""Managers for Commission models"""
import datetime

from django.db import models
from django.contrib.postgres.aggregates import ArrayAgg


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

        return self.annotate(
            commission_funds_array=ArrayAgg("commissionfund__fund_id")
        ).filter(
            commission_funds_array__contains=project_funds_list,
            commission_date__gt=today
        )
