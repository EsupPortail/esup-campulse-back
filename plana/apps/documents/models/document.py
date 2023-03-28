"""Models describing documents (charters PDF, review spreadsheets, ...)."""

import datetime

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.commissions.models.commission import Commission
from plana.apps.institutions.models.institution import Institution
from plana.storages import DynamicStorageFileField


def get_template_path(instance, filename):
    """Is used by document path_template field."""
    file_basename, extension = os.path.splitext(filename)
    year = datetime.datetime.now().strftime('%Y')
    return (
        os.path.join(
            settings.S3_TEMPLATES_FILEPATH
            if hasattr(settings, 'S3_TEMPLATES_FILEPATH')
            else '',
            year,
            f'{file_basename}{extension}',
        )
        .lower()
        .replace(' ', '_')
    )


class Document(models.Model):
    """Main model."""

    name = models.CharField(_("Name"), max_length=250, blank=False, unique=True)
    acronym = models.TextField(_("Acronym"), default="")
    description = models.TextField(_("Description"), default="")
    contact = models.TextField(_("Contact address"), blank=False)
    is_multiple = models.BooleanField(_("Is multiple"), default=False)
    days_before_expiration = models.DurationField(
        _("Days before document expiration"), default=datetime.timedelta(days=365)
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
    commission = models.ForeignKey(
        Commission,
        verbose_name=_("Commission"),
        on_delete=models.RESTRICT,
        null=True,
    )
    process_type = models.CharField(
        _("Document Status"),
        max_length=32,
        choices=[
            ("CHARTER_ASSOCIATION", _("Charter for Association")),
            (
                "CHARTER_ASSOCIATION_INSTITUTION",
                _("Charter for Association Institution"),
            ),
            ("CHARTER_PROJECT_COMMISSION", _("Charter for Project Commission")),
            ("DOCUMENT_ASSOCIATION", _("Document for Association")),
            ("DOCUMENT_USER", _("Document for User")),
            ("DOCUMENT_PROJECT", _("Document for Project")),
            ("DOCUMENT_PROJECT_REVIEW", _("Document for Project Review")),
        ],
        default="DOCUMENT_PROCESSING",
    )

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
        permissions = [
            (
                "add_document_any_commission",
                "Can add documents linked to any commission.",
            ),
            (
                "add_document_any_institution",
                "Can add documents linked to any institution.",
            ),
            (
                "delete_document_any_commission",
                "Can delete documents linked to any commission.",
            ),
            (
                "delete_document_any_institution",
                "Can delete documents linked to any institution.",
            ),
        ]
