from django import forms
from django_filters import rest_framework as filters


class NumberInFilter(filters.BaseInFilter, filters.NumberFilter):
    pass


class ChoiceInFilter(filters.BaseInFilter, filters.ChoiceFilter):
    pass


class CharInFilter(filters.BaseInFilter, filters.CharFilter):
    pass


class IntegerOrEmptyField(forms.IntegerField):
    """
    IntegerField but keeping empty string intact instead of changing it to None by default
    """
    def to_python(self, value):
        if value == "":
            return ""
        return super().to_python(value)


class EmptyNumberFilter(filters.NumberFilter):
    field_class = IntegerOrEmptyField

    def filter(self, qs, value):
        if value is None:
            return qs
        if value == "":
            return qs.filter(**{f"{self.field_name}__isnull": True})
        return qs.filter(**{self.field_name: value})
