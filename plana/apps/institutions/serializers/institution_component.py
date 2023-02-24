"""Serializers describing fields used on associations institutions components."""
from rest_framework import serializers

from plana.apps.institutions.models.institution_component import InstitutionComponent


class InstitutionComponentSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = InstitutionComponent
        fields = "__all__"
