from django_filters import rest_framework as filters

from plana.apps.institutions.models import InstitutionComponent
from plana.filters import CharInFilter, ChoiceInFilter, NumberInFilter

from .models import Document, DocumentUpload


class DocumentFilter(filters.FilterSet):

    fund_ids = NumberInFilter(field_name='fund_id', lookup_expr='in', help_text='Document fund IDs.')
    process_types = ChoiceInFilter(
        field_name='process_type', choices=Document.ProcessType.choices, help_text='Document process type.')

    class Meta:
        model = Document
        fields = [
            "acronym"
        ]


class DocumentUploadFilter(filters.FilterSet):

    process_types = CharInFilter(field_name='document__process_type')
    is_validated_by_admin = filters.BooleanFilter(field_name='validated_date', lookup_expr='isnull', exclude=True)

    class Meta:
        model = DocumentUpload
        fields = [
            'user_id',
            'association_id',
            'project_id',
        ]


class DocumentUploadFileFilter(filters.FilterSet):

    project_id = filters.NumberFilter(field_name='project_id', required=True)

    class Meta:
        model = DocumentUpload
        fields = [
            'project_id'
        ]