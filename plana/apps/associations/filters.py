from django.db.models import Count, F
from django_filters import rest_framework as filters

from plana.apps.institutions.models import InstitutionComponent
from plana.filters import EmptyNumberFilter, NumberInFilter

from .models import Association


class BaseAssociationFilter(filters.FilterSet):

    name = filters.CharFilter(method="filter_name")
    acronym = filters.CharFilter(lookup_expr="icontains")
    institutions = NumberInFilter(field_name='institution_id', lookup_expr='in')
    institution_component = EmptyNumberFilter(field_name='institution_component_id')

    def filter_name(self, queryset, name, value):
        return queryset.filter(name__nospaces__unaccent__icontains=value.replace(" ", ""))

    class Meta:
        model = Association
        fields = [
            "name",
            "acronym",
            "is_site",
            "institutions",
            "institution_component",
            "activity_field",
        ]


class AssociationFilter(BaseAssociationFilter):
    user_id = filters.NumberFilter(method='filter_user_id')

    def filter_user_id(self, queryset, name, value):
        if value and self.request.user.has_perm("users.view_user_anyone"):
            return queryset.filter(associationuser__user=value)
        return queryset

    class Meta(BaseAssociationFilter.Meta):
        fields = BaseAssociationFilter.Meta.fields + [
            "is_enabled",
            "is_public",
            "user_id"
        ]


class AssociationNameFilter(filters.FilterSet):

    institutions = NumberInFilter(field_name='institution_id', lookup_expr='in')
    allow_new_users = filters.BooleanFilter(method='filter_allow_new_users')

    def filter_allow_new_users(self, queryset, name, value):
        queryset = queryset.alias(amount_members=Count('associationuser'))
        if value:
            return queryset.filter(amount_members_allowed__gt=F('amount_members'))
        return queryset.filter(amount_members_allowed__lte=F('amount_members'))

    class Meta:
        model = Association
        fields = [
            "institutions",
            "is_public",
            "is_enabled",
            "allow_new_users"
        ]


class AssociationExportFilter(filters.FilterSet):
    associations = NumberInFilter(field_name='id', lookup_expr='in')

    class Meta:
        model = Association
        fields = [
            "associations",
        ]
