"""Models describing institutions (Crous, Unistra, UHA, ...)."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Institution(models.Model):
    """Main model."""

    name = models.CharField(_("Name"), max_length=250, blank=False)
    acronym = models.CharField(_("Acronym"), max_length=30, blank=False)
    email = models.EmailField(_("Email"), blank=False)

    def __str__(self):
        return f"{self.name} ({self.acronym})"

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")
