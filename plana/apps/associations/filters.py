from django_filters import rest_framework as filters

from django.db.models import Count, F

from plana.apps.institutions.models import InstitutionComponent
from plana.filters import EmptyNumberFilter, NumberInFilter

from .models import Association


class AssociationFilter(filters.FilterSet):

    name = filters.CharFilter(method="filter_name")
    acronym = filters.CharFilter(lookup_expr="icontains")
    is_enabled = filters.BooleanFilter(method="filter_is_enabled")
    is_public = filters.BooleanFilter(method="filter_is_public")
    institutions = NumberInFilter(field_name='institution_id', lookup_expr='in')
    institution_component = EmptyNumberFilter(field_name='institution_component_id')
    user_id = filters.NumberFilter(method='filter_user_id')

    def filter_name(self, queryset, name, value):
        return queryset.filter(name__nospaces__unaccent__icontains=value.replace(" ", ""))

    def filter_is_enabled(self, queryset, name, value):
        is_enabled = value
        request = self.request
        if request.user.is_anonymous:
            is_enabled = True
        elif not request.user.has_perm("associations.view_association_not_enabled"):
            is_enabled = True
        return queryset.filter(is_enabled=is_enabled)

    def filter_is_public(self, queryset, name, value):
        is_public = value
        request = self.request
        if request.user.is_anonymous:
            is_public = True
        elif not request.user.has_perm("associations.view_association_not_public"):
            is_public = True
        return queryset.filter(is_public=is_public)

    def filter_user_id(self, queryset, name, value):
        if value and self.request.user.has_perm("users.view_user_anyone"):
            return queryset.filter(associationuser__user=value)
        return queryset

    class Meta:
        model = Association
        fields = [
            "name",
            "acronym",
            "is_enabled",
            "is_public",
            "is_site",
            "institutions",
            "institution_component",
            "activity_field",
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
            "allow_new_users"
        ]


class AssociationExportFilter(filters.FilterSet):
    associations = NumberInFilter(field_name='id', lookup_expr='in')

    class Meta:
        model = Association
        fields = [
            "associations",
        ]
