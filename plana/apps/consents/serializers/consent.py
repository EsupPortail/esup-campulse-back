"""
Serializers describing fields used on GDPR consents.
"""
from rest_framework import serializers

from plana.apps.consents.models.consent import GDPRConsent


class GDPRConsentSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    class Meta:
        model = GDPRConsent
        fields = "__all__"
