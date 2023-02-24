"""Models describing links between GDPR consents and users (which user has given which consent and when)."""
from django.db import models
from django.utils.translation import gettext_lazy as _

from plana.apps.consents.models.consent import GDPRConsent
from plana.apps.users.models.user import User


class GDPRConsentUsers(models.Model):
    """Main model."""

    user = models.ForeignKey(User, verbose_name=_("User"), on_delete=models.CASCADE)
    consent = models.ForeignKey(
        GDPRConsent, verbose_name=_("GDPR Consent"), on_delete=models.CASCADE
    )
    date_consented = models.DateTimeField(_("Consent date"), auto_now_add=True)

    def __str__(self):
        return f"{self.user}, {self.consent}, date : {self.date_consented}"

    class Meta:
        verbose_name = _("GDPR Consent User")
        verbose_name_plural = _("GDPR Consents Users")
        permissions = []
