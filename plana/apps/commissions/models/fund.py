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
    decision_attribution_template_path = models.CharField(
        _("Decision attribution template path"), max_length=250, blank=True, null=True, default=""
    )
    attribution_template_path = models.CharField(
        _("Attribution template path"), max_length=250, blank=True, null=True, default=""
    )
    rejection_template_path = models.CharField(
        _("Rejection template path"), max_length=250, blank=True, null=True, default=""
    )
    postpone_template_path = models.CharField(
        _("Postpone template path"), max_length=250, blank=True, null=True, default=""
    )
    institution = models.ForeignKey(
        Institution,
        verbose_name=_("Institution"),
        on_delete=models.RESTRICT,
    )

    def __str__(self):
        return self.acronym

    class Meta:
        verbose_name = _("Fund")
        verbose_name_plural = _("Funds")
