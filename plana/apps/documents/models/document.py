"""Models describing documents (charters PDF, review spreadsheets, ...)."""
import datetime
import os

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.commissions.models.fund import Fund
from plana.apps.institutions.models.institution import Institution
from plana.storages import DynamicStorageFileField

if settings.USE_S3 is False:
    DynamicStorageFileField = models.FileField


def get_template_path(instance, filename):
    """Is used by document path_template field."""
    file_basename, extension = os.path.splitext(filename)
    year = datetime.datetime.now().strftime('%Y')
    return (
        os.path.join(
            settings.TEMPLATES_FILEPATH if hasattr(settings, 'TEMPLATES_FILEPATH') else '',
            year,
            f'{file_basename}{extension}',
        )
        .lower()
        .replace(' ', '_')
    )


class Document(models.Model):
    """Main model."""

    class ProcessType(models.TextChoices):
        """List of processes a document can be linked to."""

        CHARTER_ASSOCIATION = "CHARTER_ASSOCIATION", _("Charter for Association")
        CHARTER_PROJECT_FUND = "CHARTER_PROJECT_FUND", _("Charter for Project Fund")
        DOCUMENT_ASSOCIATION = "DOCUMENT_ASSOCIATION", _("Document for Association")
        DOCUMENT_USER = "DOCUMENT_USER", _("Document for User")
        DOCUMENT_PROJECT = "DOCUMENT_PROJECT", _("Document for Project")
        DOCUMENT_PROJECT_REVIEW = "DOCUMENT_PROJECT_REVIEW", _("Document for Project Review")
        NO_PROCESS = "NO_PROCESS", _("Document not linked to a process")

        @staticmethod
        def get_updatable_documents():
            """Documents with those processes can be replaced by a manager."""

            return [
                "NO_PROCESS",
                "CHARTER_ASSOCIATION",
                "CHARTER_PROJECT_FUND",
                "DOCUMENT_PROJECT",
            ]

        @staticmethod
        def get_validated_documents():
            """Documents with those processes have to be validated to be used."""

            return ["CHARTER_ASSOCIATION", "CHARTER_PROJECT_FUND"]

    name = models.CharField(_("Name"), max_length=250, default="")
    acronym = models.TextField(_("Acronym"), default="")
    description = models.TextField(_("Description"), default="")
    contact = models.TextField(_("Contact address"), default="")
    is_multiple = models.BooleanField(_("Is multiple"), default=False)
    is_required_in_process = models.BooleanField(_("Is required in process"), default=False)
    days_before_expiration = models.DurationField(_("Days before document expiration"), null=True)
    expiration_day = models.CharField(
        _("Document expiration day of the year in %m-%d format"),
        max_length=5,
        null=True,
    )
    path_template = DynamicStorageFileField(
        _("Example template file"),
        null=True,
        blank=True,
        upload_to=get_template_path,
    )
    mime_types = ArrayField(base_field=models.CharField(max_length=128), default=list)
    institution = models.ForeignKey(
        Institution,
        verbose_name=_("Institution"),
        on_delete=models.RESTRICT,
        null=True,
    )
    fund = models.ForeignKey(
        Fund,
        verbose_name=_("Fund"),
        on_delete=models.RESTRICT,
        null=True,
    )
    process_type = models.CharField(
        _("Document Status"),
        max_length=32,
        choices=ProcessType.choices,
        default="NO_PROCESS",
    )
    edition_date = models.DateTimeField(_("Edition date"), auto_now=True)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        permissions = [
            (
                "add_document_any_fund",
                "Can add documents linked to any fund.",
            ),
            (
                "add_document_any_institution",
                "Can add documents linked to any institution.",
            ),
            (
                "change_document_any_fund",
                "Can change documents linked to any fund.",
            ),
            (
                "change_document_any_institution",
                "Can change documents linked to any institution.",
            ),
            (
                "delete_document_any_fund",
                "Can delete documents linked to any fund.",
            ),
            (
                "delete_document_any_institution",
                "Can delete documents linked to any institution.",
            ),
        ]
