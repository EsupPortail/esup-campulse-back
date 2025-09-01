from django_filters import rest_framework as filters


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class ChoiceInFilter(filters.BaseInFilter, filters.ChoiceFilter):
    pass


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class EmptyNumberFilter(filters.NumberFilter):
    def filter(self, qs, value):
        if value is None:
            return qs
        if value == "":
            return qs.filter(**{f"{self.field_name}__isnull": True})
        return qs.filter(**{self.field_name: value})
