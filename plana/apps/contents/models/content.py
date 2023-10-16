"""Models describing text contents (Home, About, Contact, ...)."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Content(models.Model):
    """Main model."""

    code = models.CharField(_("Code"), max_length=128, blank=False, null=False, unique=True)
    label = models.CharField(_("Label"), max_length=128, blank=False, null=False, unique=True)
    title = models.CharField(_("Title"), max_length=512, default="")
    header = models.TextField(_("Header"), default="")
    body = models.TextField(_("Body"), blank=False, null=False)
    footer = models.TextField(_("Footer"), default="")
    aside = models.TextField(_("Sidebar"), default="")

    def __str__(self):
        return self.code

    class Meta:
        verbose_name = _("Content")
        verbose_name_plural = _("Contents")
