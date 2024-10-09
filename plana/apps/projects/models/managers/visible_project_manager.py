"""Outside of django-admin, the app only uses projects where edition_date is lower than 5 years old."""

import datetime

from django.db import models
from django.db.utils import ProgrammingError

from plana.apps.contents.models.setting import Setting


class VisibleProjectManager(models.Manager):
    """visible_objects from Project."""

    def get_queryset(self):
        """Override queryset to get project younger than defined amount of years."""
        queryset = super().get_queryset()
        invisible_projects_ids = []
        amount_years_before_project_invisibility = None
        try:
            for project in queryset:
                # TODO Tests break if this variable is set before this loop instruction. (???)
                amount_years_before_project_invisibility = Setting.get_setting(
                    "AMOUNT_YEARS_BEFORE_PROJECT_INVISIBILITY"
                )
                break
            for project in queryset:
                if datetime.datetime.now(
                    datetime.timezone(datetime.timedelta(hours=0))
                ) > project.edition_date + datetime.timedelta(days=(365 * amount_years_before_project_invisibility)):
                    invisible_projects_ids.append(project.id)
            queryset = queryset.exclude(id__in=invisible_projects_ids)
        except ProgrammingError:
            # TODO Error triggered when initial migration is applied.
            # Find a better way to manage this case.
            pass
        return queryset
