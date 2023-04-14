"""Models describing commissions dates linked to projects."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.commissions.models.commission_date import CommissionDate


class ProjectCommissionDate(models.Model):
    """Main model."""

    project = models.ForeignKey(
        "Project",
        verbose_name=_("Project"),
        on_delete=models.CASCADE,
    )
    commission_date = models.ForeignKey(
        CommissionDate,
        verbose_name=_("Commission Date"),
        on_delete=models.CASCADE,
    )
    is_first_edition = models.BooleanField(_("Is first edition"), default=True)
    amount_asked_previous_edition = models.IntegerField(
        _("Amount asked on previous edition"), default=0
    )
    amount_earned_previous_edition = models.IntegerField(
        _("Amount earned on previous edition"), default=0
    )
    amount_asked = models.IntegerField(_("Amount asked"), default=0)
    amount_earned = models.IntegerField(_("Amount earned"), default=0)
    is_validated_by_admin = models.BooleanField(
        _("Is validated by admin"), default=False
    )

    def __str__(self):
        return f"{self.project} {self.commission_date}"

    class Meta:
        verbose_name = _("Project commission date")
        verbose_name_plural = _("Projects commissions dates")
        permissions = [
            (
                "change_projectcommissiondate_basic_fields",
                "Can update basic fields between a project and a commission date.",
            ),
            (
                "change_projectcommissiondate_restricted_fields",
                "Can update restricted fields (amount earned, ...) between a project and a commission date.",
            ),
            (
                "view_projectcommissiondate_all",
                "Can view all commission dates linked to a project.",
            ),
        ]
