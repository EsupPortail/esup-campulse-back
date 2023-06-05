"""Models describing commissions."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Commission(models.Model):
    """Main model."""

    submission_date = models.DateField(_("Project submission limit date"))
    commission_date = models.DateField(_("Commission date"))
    is_open_to_projects = models.BooleanField(_("Is open to projects"), default=False)

    def __str__(self):
        return f"{self.submission_date}, {self.commission_date}, {self.is_open_to_projects}"

    class Meta:
        verbose_name = _("Commission")
        verbose_name_plural = _("Commissions")
