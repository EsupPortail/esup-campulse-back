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
    search_fields = [
        "action_title",
        "action_user__first_name",
        "action_user__last_name",
        "creation_date",
        "user__first_name",
        "user__last_name",
        "association__acronym",
        "association__name",
        "association_user__user__first_name",
        "association_user__user__last_name",
        "association_user__association__acronym",
        "association_user__association__name",
        "group_institution_fund_user__group__name",
        "group_institution_fund_user__institution__acronym",
        "group_institution_fund_user__institution__name",
        "group_institution_fund_user__fund__acronym",
        "group_institution_fund_user__fund__name",
        "group_institution_fund_user__user__first_name",
        "group_institution_fund_user__user__last_name",
        "document_upload__name",
        "document_upload__document__acronym",
        "document_upload__document__name",
        "document_upload__user__first_name",
        "document_upload__user__last_name",
        "document_upload__association__acronym",
        "document_upload__association__name",
        "document_upload__project__name",
        "project__name",
    ]
