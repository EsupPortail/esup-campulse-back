"""Models describing commissions (FSDIE, IdEx, Culture-ActionS, ...)."""
from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.institutions.models.institution import Institution


class Fund(models.Model):
    """Main model."""

    name = models.CharField(_("Name"), max_length=250, blank=False)
    acronym = models.CharField(_("Acronym"), max_length=30, blank=False)
    is_site = models.BooleanField(_("Is site"), default=settings.ASSOCIATION_IS_SITE_DEFAULT)
    institution = models.ForeignKey(
        Institution,
        verbose_name=_("Institution"),
        on_delete=models.RESTRICT,
    )

    def __str__(self):
        return f"{self.name} ({self.acronym})"

    class Meta:
        verbose_name = _("Fund")
        verbose_name_plural = _("Funds")
