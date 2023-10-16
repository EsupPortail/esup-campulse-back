from django.contrib import admin

from .models import Commission, Fund


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = ["name", "submission_date", "commission_date", "is_open_to_projects"]
    list_filter = ["is_open_to_projects"]
    search_fields = ["name", "submission_date", "commission_date"]


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = ["acronym", "name", "institution", "is_site"]
    list_filter = ["is_site"]
    search_fields = ["acronym", "name", "institution__acronym", "institution__name"]
