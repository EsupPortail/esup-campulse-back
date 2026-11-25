"""Models describing commissions."""

from django.contrib.auth import get_user_model
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.commissions import managers


class Commission(models.Model):
    """Main model."""

    submission_date = models.DateField(_("Project submission limit date"))
    commission_date = models.DateField(_("Commission date"))
    is_open_to_projects = models.BooleanField(_("Is open to projects"), default=False)
    name = models.CharField(_("Name"), max_length=250, unique=True)
    edition_date = models.DateField(_("Project edit deadline"))
    is_archived = models.BooleanField(_("Archived"), default=False)
    room = models.CharField(_("Room"), max_length=250, blank=True)
    building = models.CharField(_("Building"), max_length=250, blank=True)
    address = models.CharField(_("Address"), max_length=250, blank=True)
    scheduled_time = models.TimeField(_("Scheduled time"), blank=True, null=True)

    objects = managers.CommissionQuerySet.as_manager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = _("Commission")
        verbose_name_plural = _("Commissions")

    def get_fund_members_emails(self):
        User = get_user_model()
        funds = self.commissionfund_set.values_list("fund_id")
        return User.objects.filter(
            groupinstitutionfunduser__fund_id__in=funds,
            groupinstitutionfunduser__group__name="MEMBER_FUND"
        ).distinct().values_list("email", flat=True)
