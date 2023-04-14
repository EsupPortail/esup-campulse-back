"""Models describing documents uploaded by an association or a user."""
import datetime
import os

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.projects.models.project import Project
from plana.apps.users.models.user import User
from plana.storages import DynamicStorageFileField


def get_file_path(instance, filename):
    """Is used by document path_file field."""
    file_basename, extension = os.path.splitext(filename)
    year = datetime.datetime.now().strftime('%Y')
    return (
        os.path.join(
            settings.S3_DOCUMENTS_FILEPATH
            if hasattr(settings, 'S3_DOCUMENTS_FILEPATH')
            else '',
            year,
            f'{file_basename}{extension}',
        )
        .lower()
        .replace(' ', '_')
    )


class DocumentUpload(models.Model):
    """Main model."""

    name = models.CharField(_("Name"), max_length=250, default="")
    document = models.ForeignKey(
        "Document",
        verbose_name=_("Document"),
        on_delete=models.RESTRICT,
    )
    user = models.ForeignKey(
        User,
        verbose_name=_("User"),
        on_delete=models.RESTRICT,
        null=True,
    )
    association = models.ForeignKey(
        Association,
        verbose_name=_("Association"),
        on_delete=models.RESTRICT,
        null=True,
    )
    project = models.ForeignKey(
        Project,
        verbose_name=_("Project"),
        on_delete=models.RESTRICT,
        null=True,
    )
    upload_date = models.DateTimeField(_("Upload date"), auto_now_add=True)
    path_file = DynamicStorageFileField(
        _("Uploaded file"),
        upload_to=get_file_path,
    )
    document_upload_status = models.CharField(
        _("Document Upload Status"),
        max_length=32,
        choices=[
            ("DOCUMENT_REJECTED", _("Document Rejected")),
            ("DOCUMENT_PROCESSING", _("Document Processing")),
            ("DOCUMENT_VALIDATED", _("Document Validated")),
        ],
        default="DOCUMENT_PROCESSING",
    )

    def __str__(self):
        return f"{self.document}"

    class Meta:
        verbose_name = _("Document from association or user")
        verbose_name_plural = _("Documents from associations or users")
        permissions = [
            (
                "add_documentupload_all",
                "Can add a link from any document to any project or anu association.",
            ),
            (
                "delete_documentupload_all",
                "Can remove a link from a document to any project or any association.",
            ),
            (
                "view_documentupload_all",
                "Can view all documents linked to any project or any association.",
            ),
        ]
