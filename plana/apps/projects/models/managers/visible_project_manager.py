"""Outside of django-admin, the app only uses projects where edition_date is lower than 5 years old."""
import datetime

from django.conf import settings
from django.db import models


class VisibleProjectManager(models.Manager):
    def get_queryset(self):
        queryset = super().get_queryset()
        # TODO This breaks migrate command on new databases.
        """
        invisible_projects_ids = []
        for project in queryset:
            if datetime.datetime.now(
                datetime.timezone(datetime.timedelta(hours=0))
            ) > project.edition_date + datetime.timedelta(
                days=(365 * int(settings.AMOUNT_YEARS_BEFORE_PROJECT_INVISIBILITY))
            ):
                invisible_projects_ids.append(project.id)
        queryset = queryset.exclude(id__in=invisible_projects_ids)
        """
        return queryset
