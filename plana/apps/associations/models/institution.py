from django.db import models
from django.utils.translation import gettext_lazy as _


class Institution(models.Model):
    """
    Associations are attached to institutions (Crous, Unistra, UHA, ...).
    """

    name = models.CharField(_("Name"), max_length=250, blank=False)
    acronym = models.CharField(_("Acronym"), max_length=30, blank=False)

    def __str__(self):
        return f"{self.name} ({self.acronym})"

    class Meta:
        verbose_name = _("Institution")
        verbose_name_plural = _("Institutions")