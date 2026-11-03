"""Admin view for Document models."""
import datetime

from django import forms
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Prefetch
from django.utils.translation import gettext_lazy as _

from .models import Document, DocumentUpload
from ..associations.models import Association


class DocumentAdminForm(forms.ModelForm):
    """Custom admin form for Document model to manage updates rules on objects."""
    def __init__(self, *args, **kwargs):
        # Retrieve request from ModelAdmin
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        """
        Custom clean to block a Document process to be changed by a non-superuser if some documents were already uploaded.
        """
        cleaned_data = super().clean()

        # Only when change on object
        if self.instance and self.instance.pk:
            old_obj = Document.objects.get(pk=self.instance.pk)
            uploaded_docs = DocumentUpload.objects.filter(document=old_obj).exists()

            new_process_type = cleaned_data.get('process_type')

            if uploaded_docs and old_obj.process_type != new_process_type:
                if self.request and not self.request.user.is_superuser:
                    raise ValidationError(
                        _("Cannot update this document's process : some documents using it were already uploaded.")
                    )

        return cleaned_data


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """List view for documents."""

    form = DocumentAdminForm
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

    def get_form(self, request, obj=None, change=False, **kwargs):
        """Custom get_form method to pass request data"""
        FormClass = super().get_form(request, obj, **kwargs)

        class ModelFormWithRequest(FormClass):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return FormClass(*args, **kwargs)

        return ModelFormWithRequest

    def has_delete_permission(self, request, obj=None):
        """
        Custom admin permission to avoid non-superusers from deleting documents
        if some uploads were already wade using them.
        """
        if request.user.is_superuser:
            return True
        # Cannot mass-delete documents if not superuser anymore
        if obj is None:
            return False
        # Conditionally mask the delete button in change form
        if DocumentUpload.objects.filter(document=obj).exists():
            return False

        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        """
        Custom save method to update future charter expiration date of all associations in advanced workflow
        with the new expiration day.
        """
        old_obj = Document.objects.filter(pk=obj.pk).first()
        super().save_model(request, obj, form, change)

        if change and old_obj:
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
