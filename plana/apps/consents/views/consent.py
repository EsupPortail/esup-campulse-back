from rest_framework import generics

from plana.apps.consents.models.consent import GDPRConsent
from plana.apps.consents.serializers.consent import GDPRConsentSerializer


class GDPRConsentList(generics.ListAPIView):
    """
    GET : Lists all GDPR types of consents.
    """

    serializer_class = GDPRConsentSerializer

    def get_queryset(self):
        return GDPRConsent.objects.all().order_by("title")
