"""Admin view for Document models."""
import datetime

from django.contrib import admin
from django.db.models import Prefetch

from .models import Document, DocumentUpload
from ..associations.models import Association


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """List view for documents."""

    list_display = [
        "acronym",
        "description",
        "max_uploads",
        "is_required_in_process",
        "institution",
        "fund",
        "process_type",
    ]
    list_filter = ["max_uploads", "is_required_in_process"]
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

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('fund', 'institution')

    def save_model(self, request, obj, form, change):
        """
        Custom save method to update future charter expiration date of all associations in advanced workflow
        with the new expiration day.
        """
        if change:
            old_obj = Document.objects.get(pk=obj.pk)
            super().save_model(request, obj, form, change)

            if old_obj.expiration_day != obj.expiration_day and obj.acronym == "CHARTE_SITE":
                latest_uploads = DocumentUpload.objects.filter(
                    document__process_type="CHARTER_ASSOCIATION",
                    document__acronym="CHARTE_SITE"
                ).order_by('-validated_date')

                affected_associations = Association.objects.filter(
                    charter_status__in=["CHARTER_PROCESSING", "CHARTER_DRAFT_PROCESSED", "CHARTER_VALIDATED"],
                    charter_date__gte=datetime.date.today()
                ).prefetch_related(
                    Prefetch(
                        'documentupload_set',
                        queryset=latest_uploads,
                        to_attr='latest_charter_uploads'
                    )
                )

                associations_to_update = []
                for asso in affected_associations:
                    if asso.latest_charter_uploads:
                        last_upload = asso.latest_charter_uploads[0]
                        new_date = last_upload.calculated_expiration_date
                        asso.charter_date = new_date
                        if not new_date:
                            asso.charter_status = "CHARTER_DRAFT"
                        associations_to_update.append(asso)
                if associations_to_update:
                    Association.objects.bulk_update(associations_to_update, ["charter_date", "charter_status"])


@admin.register(DocumentUpload)
class DocumentUploadAdmin(admin.ModelAdmin):
    """List view for document uploads."""

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

    def get_queryset(self, request):
        return (
            super().get_queryset(request)
            .select_related('document', 'user', 'association', 'project')
        )
