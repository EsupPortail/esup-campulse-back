"""Models describing text contents (Home, About, Contact, ...)."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Content(models.Model):
    """Main model."""

    code = models.CharField(
        _("Code"), max_length=128, blank=False, null=False, unique=True
    )
    label = models.CharField(
        _("Label"), max_length=128, blank=False, null=False, unique=True
    )
    header = models.TextField(_("Header"), default="")
    body = models.TextField(_("Body"), blank=False, null=False)
    footer = models.TextField(_("Footer"), default="")

    def __str__(self):
        return f"{self.code} : {self.label}"

    class Meta:
        verbose_name = _("Content")
        verbose_name_plural = _("Contents")
