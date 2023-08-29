"""Models describing footer logos."""
import datetime
import os

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.storages import DynamicStorageFileField

if settings.USE_S3 is False:
    DynamicStorageFileField = models.FileField


def get_logo_path(instance, filename):
    """Is used by path_logo field."""
    file_basename, extension = os.path.splitext(filename)
    year = datetime.datetime.now().strftime('%Y')
    return (
        os.path.join(
            settings.LOGOS_FILEPATH if hasattr(settings, 'LOGOS_FILEPATH') else '',
            year,
            f'{file_basename}{extension}',
        )
        .lower()
        .replace(' ', '_')
    )


class Logo(models.Model):
    """Main model."""

    acronym = models.TextField(_("Acronym"), default="")
    title = models.TextField(_("Logo alt"), default="")
    url = models.TextField(_("Site URL"), default="")
    path_logo = DynamicStorageFileField(
        _("Dynamic thumbnails for the logo"),
        null=True,
        blank=True,
        upload_to=get_logo_path,
    )
    visible = models.BooleanField(_("Is visible"), default=False)

    def __str__(self):
        return f"{self.title} : {self.acronym}"

    class Meta:
        verbose_name = _("Logo")
        verbose_name_plural = _("Logos")