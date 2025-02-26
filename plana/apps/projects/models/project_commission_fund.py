"""Models describing commissions dates linked to projects."""
import datetime
import os

from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.commissions.models.commission_fund import CommissionFund
from plana.storages import DynamicStorageFileField

if settings.USE_S3 is False:
    DynamicStorageFileField = models.FileField


def get_file_path(instance, filename):
    """Is used by ProjectCommissionFund last_notification_file field."""
    file_basename, extension = os.path.splitext(filename)
    year = datetime.datetime.now().strftime('%Y')
    return (
        os.path.join(
            settings.S3_DOCUMENTS_FILEPATH if hasattr(settings, 'S3_DOCUMENTS_FILEPATH') else '',
            year,
            f'{file_basename}{extension}',
        )
        .lower()
        .replace(' ', '_')
    )


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
    amount_asked_previous_edition = models.PositiveIntegerField(_("Amount asked on previous edition"), default=0)
    amount_earned_previous_edition = models.PositiveIntegerField(_("Amount earned on previous edition"), default=0)
    amount_asked = models.PositiveIntegerField(_("Amount asked"), default=0)
    amount_earned = models.PositiveIntegerField(_("Amount earned"), default=None, null=True)
    is_validated_by_admin = models.BooleanField(_("Is validated by admin"), default=None, null=True)
    last_notification_file = DynamicStorageFileField(_("Last notification file"), blank=True, validators=[FileExtensionValidator(["pdf"])])

    def __str__(self):
        return f"{self.project} - {self.commission_fund}"

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
                "view_projectcommissionfund_any_fund",
                "Can view all commission funds linked to all projects for a commission.",
            ),
            (
                "view_projectcommissionfund_any_institution",
                "Can view all commission funds linked to all projects for an institution.",
            ),
        ]
