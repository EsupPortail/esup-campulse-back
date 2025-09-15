from django_filters import rest_framework as filters

from plana.filters import ChoiceInFilter
from .models import Project, ProjectCommissionFund


class ProjectFilter(filters.FilterSet):

    name = filters.CharFilter(method="filter_name")
    year = filters.NumberFilter(field_name="creation_date", lookup_expr="year")
    manual_identifier = filters.CharFilter(method="filter_manual_identifier")
    commission_id = filters.NumberFilter(field_name="projectcommissionfund__commission_fund__commission_id")
    project_statuses = ChoiceInFilter(
        field_name='project_status',
        choices=Project.ProjectStatus.choices,
        help_text="Filter by Project Statuses codes."
    )
    with_comments = filters.BooleanFilter(
        field_name="projects",
        lookup_expr="isnull",
        help_text="Filter to get projects where comments are posted.",
        exclude=True
    )
    active_projects = filters.BooleanFilter(
        method="filter_active_projects",
        help_text="Filter to get projects where reviews are still pending.",
    )

    def filter_name(self, queryset, name, value):
        return queryset.filter(name__nospaces__unaccent__icontains=value.replace(" ", ""))

    def filter_manual_identifier(self, queryset, name, value):
        return queryset.filter(manual_identifier__nospaces__unaccent__icontains=value.replace(" ", ""))

    def filter_active_projects(self, queryset, name, value):
        inactive_statuses = Project.ProjectStatus.get_archived_project_statuses()
        if value:
            return queryset.exclude(project_status__in=inactive_statuses)
        else:
            return queryset.filter(project_status__in=inactive_statuses)

    class Meta:
        model = Project
        fields = [
            "user_id",
            "association_id",
        ]


class ProjectCommissionFundFilter(filters.FilterSet):

    commission_id = filters.NumberFilter(field_name="commission_fund__commission_id")

    class Meta:
        model = ProjectCommissionFund
        fields = [
            'project_id'
        ]
