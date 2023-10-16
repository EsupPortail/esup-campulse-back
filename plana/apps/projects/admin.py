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

    @admin.display(description=_("Association User"))
    @admin.display(ordering="association_user")
    def get_association_user(self, obj):
        """Get user that manages a project in an association."""
        if obj.association_user is not None:
            user = User.objects.get(id=AssociationUser.objects.get(id=obj.association_user.id).user_id)
            return f"{user.first_name} {user.last_name}"
        return "-"

    @admin.display(description=_("Project commission fund"))
    @admin.display(ordering="projectcommissionfund")
    def get_commission_funds(self, obj):
        """Get commissions and funds linked to a project."""
        project_commission_funds = ProjectCommissionFund.objects.filter(project_id=obj.id)
        if project_commission_funds.count() > 0:
            commission_name = project_commission_funds.first().commission_fund.commission.name
            fund_names = list(project_commission_funds.values_list("commission_fund__fund__acronym", flat=True))
            return f"{commission_name} - {', '.join(fund_names)}"
        return "-"


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
