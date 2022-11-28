from functools import reduce

from django.db import models
from django.db.models import Count


class MailTemplateVarQuerySet(models.QuerySet):

    def fakevar_counts(self):
        queryset = super()
        return reduce(
            lambda acc, b: acc.annotate(**{f'{b}_cnt': Count(b, distinct=True)}),
            self.model.fakevars_relations_names(),
            queryset)
