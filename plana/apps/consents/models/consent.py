"""Models describing GDPR types of consents."""
from django.db import models
from django.utils.translation import gettext_lazy as _


class GDPRConsent(models.Model):
    """Main model."""

    title = models.CharField(_("GDPR Consent title"), max_length=256, blank=False)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = _("GDPR Consent")
        verbose_name_plural = _("GDPR Consents")
