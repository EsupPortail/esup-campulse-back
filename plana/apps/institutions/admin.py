"""Admin view for Institution models."""

from django.contrib import admin
from django.contrib.auth.models import Group

from plana.apps.users.models.user import GroupInstitutionFundUser

from .models import Institution, InstitutionComponent


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    """List view for institutions."""

    list_display = ["acronym", "name"]
    search_fields = ["acronym", "name"]

    def save_model(self, request, obj, form, change):
        """Add new group to MANAGER_GENERAL when an Institution is created."""
        super().save_model(request, obj, form, change)
        group = Group.objects.get(name="MANAGER_GENERAL")
        user_ids = GroupInstitutionFundUser.objects.filter(group_id=group.id).values_list("user_id", flat=True)
        for user_id in list(set(user_ids)):
            GroupInstitutionFundUser.objects.create(user_id=user_id, group_id=group.id, institution_id=obj.id)


@admin.register(InstitutionComponent)
class InstitutionComponentAdmin(admin.ModelAdmin):
    """List view for institution components."""

    list_display = ["name", "institution"]
    search_fields = ["name", "institution__acronym", "institution__name"]
