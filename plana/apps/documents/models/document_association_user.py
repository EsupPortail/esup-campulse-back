"""Models describing documents uploaded by an association or a user."""

import datetime

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


class DocumentAssociationUser(models.Model):
    """Main model."""

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
    status = models.CharField(
        _("Status"),
        max_length=32,
        choices=[
            ("DOCUMENT_REJECTED", _("Document Rejected")),
            ("DOCUMENT_PROCESSING", _("Document Processing")),
            ("DOCUMENT_VALIDATED", _("Document Validated")),
        ],
        default="DOCUMENT_PROCESSING",
    )

    def __str__(self):
        return f"{self.document} : {self.association} {self.user}"

    class Meta:
        verbose_name = _("Document from association or user")
        verbose_name_plural = _("Documents from associations or users")