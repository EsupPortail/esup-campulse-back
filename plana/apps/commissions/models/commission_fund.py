"""Models describing commissions."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class CommissionFund(models.Model):
    """Main model."""

    commission = models.ForeignKey(
        "Commission",
        verbose_name=_("Commission"),
        on_delete=models.RESTRICT,
    )
    fund = models.ForeignKey(
        "Fund",
        verbose_name=_("Fund"),
        on_delete=models.RESTRICT,
    )

    def __str__(self):
        return f"{self.commission}, {self.fund}"

    class Meta:
        verbose_name = _("Commission Fund")
        verbose_name_plural = _("Commissions Funds")
