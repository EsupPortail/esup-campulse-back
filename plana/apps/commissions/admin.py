from django.contrib import admin

from .models import Commission, Fund


@admin.register(Commission)
class CommissionAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "submission_date",
        "commission_date",
        "is_open_to_projects",
    ]


@admin.register(Fund)
class FundAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "acronym",
        "institution",
        "is_site",
    ]
