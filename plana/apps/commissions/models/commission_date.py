"""Models describing commissions dates."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class Commission(models.Model):
    """Main model."""

    submission_date = models.DateField(_("Project submission limit date"))
    commission_date = models.DateField(_("Commission date"))
    commission = models.ForeignKey(
        "Fund",
        verbose_name=_("Fund"),
        on_delete=models.RESTRICT,
    )

    def __str__(self):
        return f"{self.submission_date}, {self.commission_date}"

    class Meta:
        verbose_name = _("Commission Date")
        verbose_name_plural = _("Commissions Dates")
