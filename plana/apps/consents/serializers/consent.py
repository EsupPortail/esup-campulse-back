from rest_framework import serializers

from plana.apps.consents.models.consent import GDPRConsent


class GDPRConsentSerializer(serializers.ModelSerializer):
    class Meta:
        model = GDPRConsent
        fields = "__all__"
