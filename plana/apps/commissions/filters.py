"""Filters for commissions app views"""

from django_filters import rest_framework as filters
from django.db.models import Q

from plana.apps.commissions.models import Commission
from plana.apps.projects.models import Project
from plana.filters import NumberInFilter


class CommissionFilter(filters.FilterSet):
    """Main FilterSet class for Commissions list"""
    is_site = filters.BooleanFilter(field_name="commissionfund__fund__is_site")
    funds = NumberInFilter(field_name="commissionfund__fund_id", lookup_expr="in")
    with_active_projects = filters.BooleanFilter(method="filter_with_active_projects")
    only_with_active_projects = filters.BooleanFilter(method="filter_only_with_active_projects")
    managed_projects = filters.BooleanFilter(method="filter_managed_projects")

    class Meta:
        model = Commission
        fields = ["is_open_to_projects"]
        distinct = True

    def filter_with_active_projects(self, queryset, name, value):
        """
        Filter commissions with archived projects/no projects if false
        Filter commissions with active projects/no projects if true
        "Filter to get commissions where projects reviews are still pending or not."
        """
        archived_statuses = (Project.ProjectStatus.get_archived_project_statuses())
        active_projects_ids = Project.visible_objects.exclude(project_status__in=Project.ProjectStatus.get_archived_project_statuses()).values_list("id", flat=True)
        if value:
            return queryset.filter(
                Q(commissionfund__projectcommissionfund__project_id__in=active_projects_ids)
                | Q(commissionfund__projectcommissionfund__isnull=True)
            )
        else:
            return queryset.filter(
                Q(commissionfund__projectcommissionfund__project__project_status__in=archived_statuses)
                | Q(commissionfund__projectcommissionfund__isnull=True)
            )

    def filter_only_with_active_projects(self, queryset, name, value):
        """
        Filter commissions with only archived projects if false
        Filter commissions with ONLY active projects if true
        "Filter to get commission_dates where projects reviews are still pending exclusively."
        """
        archived_statuses = Project.ProjectStatus.get_archived_project_statuses()

        commissions_with_archived = Commission.objects.filter(
            commissionfund__projectcommissionfund__project__project_status__in=archived_statuses
        ).values_list("id", flat=True)

        commissions_with_active = Commission.objects.filter(
            commissionfund__projectcommissionfund__project__in=Project.visible_objects.exclude(project_status__in=archived_statuses)
        ).values_list("id", flat=True)

        if value:
            return queryset.filter(id__in=commissions_with_active).exclude(id__in=commissions_with_archived)
        else:
            return queryset.filter(id__in=commissions_with_archived).exclude(id__in=commissions_with_active)

    def filter_managed_projects(self, queryset, name, value):
        """
        If true, filters commissions based on user management permissions, if false, exclude those
        "Filter to get commissions with projects managed by the current user."
        """
        user = self.request.user
        if not user or user.is_anonymous:
            return queryset

        visible_managed_project_ids = Project.visible_objects.filter(
            association__in=user.get_user_managed_associations()
        ).values_list("id", flat=True)
        is_managed_condition = Q(
            commissionfund__projectcommissionfund__project_id__in=visible_managed_project_ids
        ) | Q(commissionfund__fund__in=user.get_user_managed_funds())

        if value:
            return queryset.filter(is_managed_condition).distinct()
        else:
            return queryset.exclude(is_managed_condition).distinct()
