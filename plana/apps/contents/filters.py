from django_filters import rest_framework as filters

from plana.filters import CharInFilter
from .models import Content


class ContentFilter(filters.FilterSet):

    codes = CharInFilter(field_name='code', lookup_expr='in')

    class Meta:
        model = Content
        fields = [
            "code",
            "is_editable"
        ]
