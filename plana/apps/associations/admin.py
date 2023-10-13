from django.contrib import admin

from .models import ActivityField, Association

admin.site.register(ActivityField)


@admin.register(Association)
class AssociationAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "acronym",
        "email",
        "institution",
        "is_enabled",
        "is_public",
        "is_site",
        "charter_status",
        "can_submit_projects",
    ]
