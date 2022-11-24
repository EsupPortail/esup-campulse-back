from django.db import models
from django.utils.translation import gettext as _


class GDPRConsent(models.Model):
    """
    Model that lists GDPR types of consents.
    """

    title = models.CharField(_("GDPR Consent title"), max_length=256, blank=False)

    def __str__(self):
        return f"{self.title}"

    class Meta:
        verbose_name = _("GDPR Consent")
        verbose_name_plural = _("GDPR Consents")
