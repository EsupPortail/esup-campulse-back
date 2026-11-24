"""Filters for commissions app views"""
from django.utils import timezone
from django_filters import rest_framework as filters

from plana.apps.commissions.models import Commission
from plana.filters import NumberInFilter


class CommissionFilter(filters.FilterSet):
    """Main FilterSet class for Commissions list"""
    is_site = filters.BooleanFilter(field_name="commissionfund__fund__is_site")
    funds = NumberInFilter(field_name="commissionfund__fund_id", lookup_expr="in")
    with_closed_future_commissions = filters.BooleanFilter(method="filter_with_closed_future_commissions")
    to_postpone_project = filters.NumberFilter(method="filter_to_postpone_project")
    commission_date = filters.DateFromToRangeFilter()
    edition_date = filters.DateFromToRangeFilter()
    submission_date = filters.DateFromToRangeFilter()
    name = filters.CharFilter(lookup_expr="icontains")

    class Meta:
        model = Commission
        fields = ["is_open_to_projects", "is_archived"]
        distinct = True

    def filter_with_closed_future_commissions(self, queryset, name, value):
        """
        Boolean filter with two specific filtering for display purposes
        False : Exclude future commissions not open_to_projects yet
        True : Does nothing, can contain all commissions including future ones not open_to_projects yet
        """
        if value or value is None:
            return queryset
        return queryset.exclude(is_open_to_projects=False, commission_date__gte=timezone.localdate())

    def filter_to_postpone_project(self, queryset, name, value):
        """
        Filtering commissions that can welcome the designated project id
        If no project given, do nothing
        """
        if value:
            return queryset.allowing_project_postpone(value)
        return queryset
