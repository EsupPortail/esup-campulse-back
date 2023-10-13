from django.contrib import admin

from .models import ActivityField, Association


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
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


@admin.register(ActivityField)
class ActivityFieldAdmin(admin.ModelAdmin):
    list_display = [
        "name",
    ]
