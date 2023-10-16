from django.contrib import admin

from .models import Document, DocumentUpload


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = [
        "acronym",
        "description",
        "is_multiple",
        "is_required_in_process",
        "institution",
        "fund",
        "process_type",
    ]
    list_filter = ["is_multiple", "is_required_in_process"]
    search_fields = [
        "acronym",
        "name",
        "description",
        "institution__acronym",
        "institution__name",
        "fund__acronym",
        "fund__name",
        "process_type",
    ]


@admin.register(DocumentUpload)
class DocumentUploadAdmin(admin.ModelAdmin):
    list_display = ["name", "document", "user", "association", "project"]
    search_fields = [
        "name",
        "document__acronym",
        "document__name",
        "user__first_name",
        "user__last_name",
        "association__acronym",
        "association__name",
        "project__name",
    ]
