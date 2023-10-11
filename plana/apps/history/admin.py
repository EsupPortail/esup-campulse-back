from django.contrib import admin

from .models import History


@admin.register(History)
class HistoryAdmin(admin.ModelAdmin):
    list_display = [
        "action_title",
        "action_user",
        "creation_date",
        "user",
        "association",
        "association_user",
        "group_institution_fund_user",
        "document_upload",
        "project",
    ]
