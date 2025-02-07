"""Admin view for Project models."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from plana.apps.users.models.user import AssociationUser, User

from .models import (
    Category,
    Project,
    ProjectCategory,
    ProjectComment,
    ProjectCommissionFund,
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """List view for categories."""

    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """List view for projects."""

    list_display = [
        "name",
        "manual_identifier",
        "user",
        "association",
        "get_association_user",
        "project_status",
        "get_commission_funds",
    ]
    search_fields = [
        "name",
        "manual_identifier",
        "user__first_name",
        "user__last_name",
        "association__acronym",
        "association__name",
        "association_user__user__first_name",
        "association_user__user__last_name",
        "project_status",
    ]

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('user', 'association_user__user', 'association')
            .prefetch_related(
                'projectcommissionfund_set__commission_fund__commission',
                'projectcommissionfund_set__commission_fund__fund'
            )
        )

    @admin.display(description=_("Association User"))
    @admin.display(ordering="association_user")
    def get_association_user(self, obj):
        """Get user that manages a project in an association."""
        if (association_user := obj.association_user):
            user = association_user.user
            return f"{user.first_name} {user.last_name}"
        return "-"

    @admin.display(description=_("Project commission fund"))
    @admin.display(ordering="projectcommissionfund")
    def get_commission_funds(self, obj):
        """Get commissions and funds linked to a project."""
        commission_name = ''
        fund_names = []
        for pcf in obj.projectcommissionfund_set.all():
            commision_fund = pcf.commission_fund
            commission_name = commision_fund.commission.name
            fund_names.append(commision_fund.fund.acronym)
        if commission_name:
            return f"{commission_name} - {', '.join(fund_names)}"
        return '-'


@admin.register(ProjectCategory)
class ProjectCategoryAdmin(admin.ModelAdmin):
    """List view for project categories."""

    list_display = ["category", "project"]
    search_fields = ["category__name", "project__name"]


@admin.register(ProjectComment)
class ProjectCommentAdmin(admin.ModelAdmin):
    """List view for project comments."""

    list_display = ["text", "is_visible", "project", "user"]
    list_filter = ["is_visible"]
    search_fields = ["text", "project__name", "user__first_name", "user__last_name"]

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('project', 'user')


@admin.register(ProjectCommissionFund)
class ProjectCommissionFundAdmin(admin.ModelAdmin):
    """List view for project commission funds."""

    list_display = ["project", "commission_fund", "is_validated_by_admin"]
    list_filter = ["is_validated_by_admin"]
    search_fields = [
        "project__name",
        "commission_fund__commission__name",
        "commission_fund__fund__acronym",
        "commission_fund__fund__name",
    ]
