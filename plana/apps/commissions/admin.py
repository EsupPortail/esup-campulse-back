"""Admin view for Commission models."""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Commission, CommissionFund, Fund


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    """List view for commissions."""

    list_display = ["name", "submission_date", "commission_date", "is_open_to_projects", "get_funds"]
    list_filter = ["is_open_to_projects"]
    search_fields = ["name", "submission_date", "commission_date"]

    @admin.display(description=_("Funds"))
    @admin.display(ordering="commissionfund")
    def get_funds(self, obj):
        """Get funds linked to a commission."""
        return list(CommissionFund.objects.filter(commission_id=obj.id).values_list("fund__acronym", flat=True))


@admin.register(CommissionFund)
class CommissionFundAdmin(admin.ModelAdmin):
    """List view for commission funds."""

    list_display = ["commission", "fund"]
    search_fields = ["commission__name", "fund__acronym"]


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    """List view for funds."""

    list_display = ["acronym", "name", "institution", "is_site"]
    list_filter = ["is_site"]
    search_fields = ["acronym", "name", "institution__acronym", "institution__name"]
