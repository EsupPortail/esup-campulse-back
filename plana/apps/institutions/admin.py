from django.contrib import admin

from .models import Institution, InstitutionComponent


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    list_display = ["acronym", "name"]
    search_fields = ["acronym", "name"]


@admin.register(InstitutionComponent)
class InstitutionComponentAdmin(admin.ModelAdmin):
    list_display = ["name", "institution"]
    search_fields = ["name", "institution__acronym", "institution__name"]
