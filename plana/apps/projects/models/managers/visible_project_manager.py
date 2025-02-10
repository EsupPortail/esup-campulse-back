"""Outside of django-admin, the app only uses projects where edition_date is lower than 5 years old."""

import datetime

from django.apps import apps
from django.db import models
from django.db.utils import ProgrammingError


class VisibleProjectManager(models.Manager):
    """visible_objects from Project."""

    def get_queryset(self):
        """Override queryset to get project younger than defined amount of years."""
        queryset = super().get_queryset()

        Setting = apps.get_model('contents', 'Setting')
        invisible_projects_ids = []

        try:
            days_before_project_invisibility = 365 * Setting.get_setting(
                "AMOUNT_YEARS_BEFORE_PROJECT_INVISIBILITY"
            )
            for project in queryset:
                if datetime.datetime.now(
                    datetime.timezone(datetime.timedelta(hours=0))
                ) > project.edition_date + datetime.timedelta(days=(365 * days_before_project_invisibility)):
                    invisible_projects_ids.append(project.id)
            return queryset.exclude(id__in=invisible_projects_ids)
        except Exception:
            # TODO Error triggered when initial migration is applied
            # and AMOUNT_YEARS_BEFORE_PROJECT_INVISIBILITY is empty
            return queryset
