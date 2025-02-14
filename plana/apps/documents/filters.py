from django_filters import rest_framework as filters

from plana.filters import ChoiceInFilter, NumberInFilter
from plana.apps.institutions.models import InstitutionComponent
from .models import Document


class DocumentFilter(filters.FilterSet):

    fund_ids = NumberInFilter(field_name='fund_id', lookup_expr='in', help_text='Document fund IDs.')
    process_types = ChoiceInFilter(
        field_name='process_type', choices=Document.ProcessType.choices, help_text='Document process type.')

    class Meta:
        model = Document
        fields = [
            "acronym"
        ]
