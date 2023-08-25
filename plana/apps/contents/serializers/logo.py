"""Serializers describing fields used on logos."""
from rest_framework import serializers

from plana.apps.contents.models.logo import Logo


class LogoSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Logo
        fields = "__all__"
