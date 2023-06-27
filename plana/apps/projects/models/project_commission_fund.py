"""Models describing commissions dates linked to projects."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.commissions.models.commission_fund import CommissionFund


class ProjectCommissionFund(models.Model):
    """Main model."""

    project = models.ForeignKey(
        "Project",
        verbose_name=_("Project"),
        on_delete=models.CASCADE,
    )
    commission_fund = models.ForeignKey(
        CommissionFund,
        verbose_name=_("Commission Fund"),
        on_delete=models.CASCADE,
    )
    is_first_edition = models.BooleanField(_("Is first edition"), default=True)
    amount_asked_previous_edition = models.PositiveIntegerField(
        _("Amount asked on previous edition"), default=0
    )
    amount_earned_previous_edition = models.PositiveIntegerField(
        _("Amount earned on previous edition"), default=0
    )
    amount_asked = models.PositiveIntegerField(_("Amount asked"), default=0)
    amount_earned = models.PositiveIntegerField(
        _("Amount earned"), default=None, null=True
    )
    is_validated_by_admin = models.BooleanField(
        _("Is validated by admin"), default=False
    )

    def __str__(self):
        return f"{self.project} {self.commission_fund}"

    class Meta:
        verbose_name = _("Project commission fund")
        verbose_name_plural = _("Projects commissions funds")
        permissions = [
            (
                "change_projectcommissionfund_as_bearer",
                "Can update bearer fields (amount asked) between a project and a commission fund.",
            ),
            (
                "change_projectcommissionfund_as_validator",
                "Can update validator fields (amount earned) between a project and a commission fund.",
            ),
            (
                "view_projectcommissionfund_any_commission",
                "Can view all commission funds linked to all projects for a commission.",
            ),
            (
                "view_projectcommissionfund_any_institution",
                "Can view all commission funds linked to all projects for an institution.",
            ),
        ]
