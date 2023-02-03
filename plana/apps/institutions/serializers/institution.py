"""
Serializers describing fields used on associations institutions.
"""
from rest_framework import serializers

from plana.apps.institutions.models.institution import Institution


class InstitutionSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    class Meta:
        model = Institution
        fields = "__all__"
