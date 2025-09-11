"""Filters for user app views"""

from django_filters import rest_framework as filters

from plana.filters import NumberInFilter

from .models import AssociationUser


class AssociationUserFilter(filters.FilterSet):
    is_validated_by_admin = filters.BooleanFilter()
    institutions = NumberInFilter(field_name='association__institution_id', lookup_expr='in')
    association_id = filters.NumberFilter(method='filter_association_id')

    def filter_association_id(self, queryset, name, value):
        if (
            value
            and (
                self.request.user.has_perm("users.view_associationuser_anyone")
                or self.request.user.is_president_in_association(value)
            )
        ):
            return queryset.filter(association_id=value)
        return queryset

    class Meta:
        model = AssociationUser
        fields = [
            "is_validated_by_admin",
            "institutions",
            "association_id"
        ]
