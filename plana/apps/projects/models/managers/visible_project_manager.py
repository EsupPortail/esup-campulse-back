"""Outside of django-admin, the app only uses projects where edition_date is lower than 5 years old."""
import datetime

from django.conf import settings
from django.db import models
from django.db.utils import ProgrammingError


class VisibleProjectManager(models.Manager):
    """visible_objects from Project."""

    def get_queryset(self):
        """Override queryset to get project younger than defined amount of years."""
        queryset = super().get_queryset()
        invisible_projects_ids = []
        try:
            for project in queryset:
                if datetime.datetime.now(
                    datetime.timezone(datetime.timedelta(hours=0))
                ) > project.edition_date + datetime.timedelta(
                    days=(365 * int(settings.AMOUNT_YEARS_BEFORE_PROJECT_INVISIBILITY))
                ):
                    invisible_projects_ids.append(project.id)
            queryset = queryset.exclude(id__in=invisible_projects_ids)
        except ProgrammingError:
            # TODO Error triggered when initial migration is applied.
            # Find a better way to manage this case.
            pass
        return queryset
