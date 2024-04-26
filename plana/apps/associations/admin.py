"""Admin view for Association models."""

from django.contrib import admin

from .models import ActivityField, Association


@admin.register(ActivityField)
class ActivityFieldAdmin(admin.ModelAdmin):
    """List view for activity fields."""

    list_display = ["name"]
    search_fields = ["name"]


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    """List view for associations."""

    list_display = [
        "acronym",
        "name",
        "email",
        "institution",
        "is_enabled",
        "is_public",
        "is_site",
        "charter_status",
        "can_submit_projects",
    ]
    list_filter = ["is_enabled", "is_public", "is_site", "can_submit_projects"]
    search_fields = ["acronym", "name", "email", "institution__acronym", "institution__name", "charter_status"]
