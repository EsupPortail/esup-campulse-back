"""Admin view for Content models."""

from django.contrib import admin

from .models import Content, Logo, Setting


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    """List view for contents."""

    list_display = ["code", "label"]
    search_fields = ["code", "label", "title", "header", "body", "footer", "aside"]


@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    """List view for logos."""

    list_display = ["acronym", "title", "url", "visible"]
    list_filter = ["visible"]
    search_fields = ["acronym", "title"]

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.exclude(row=2)

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.append("row")
        return fields


@admin.register(Setting)
class SettingAdmin(admin.ModelAdmin):
    """List view for settings."""

    list_display = ["setting", "parameters"]
