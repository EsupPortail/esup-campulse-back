"""Models describing documents (charters PDF, review spreadsheets, ...)."""

import datetime

from django.conf import settings
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import gettext_lazy as _

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

    name = models.CharField(_("Name"), max_length=250, blank=False)
    description = models.TextField(_("Description"), default="")
    contact = models.TextField(_("Contact address"), blank=False)
    is_multiple = models.BooleanField(_("Is multiple"), default=False)
    days_before_expiration = models.DurationField(
        _("Days before document expiration"), default=datetime.timedelta(days=365)
    )
    """
    # TODO Debug path_template field with fixtures.
    path_template = DynamicStorageFileField(
        _("Example template file"),
        null=True,
        blank=True,
        upload_to=get_template_path,
    )
    """
    mime_types = ArrayField(base_field=models.CharField(max_length=128), default=list)

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
