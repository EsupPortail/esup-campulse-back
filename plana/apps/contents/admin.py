"""Admin view for Content models."""

from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin

from .models import Content, Logo, Setting


@admin.register(Content)
class ContentAdmin(SummernoteModelAdmin):
    """List view for contents."""

    list_display = ["code", "label"]
    search_fields = ["code", "label", "title", "header", "body", "footer", "aside"]
    summernote_fields = ("header", "body", "footer", "aside")

    def get_readonly_fields(self, request, obj=None):
        fields = list(super().get_readonly_fields(request))
        if not request.user.is_superuser:
            fields.extend(["is_editable"])
            if not obj.code.startswith("NOTIFICATION_"):
                fields.extend(["code", "label"])
        return fields

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.exclude(is_editable=True)


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
