"""Serializers describing fields used on logos."""
from django.conf import settings
from rest_framework import serializers

from plana.apps.contents.models.logo import Logo


class LogoSerializer(serializers.ModelSerializer):
    """Main serializer."""

    path_logo = serializers.SerializerMethodField("cached_logo_url")

    def cached_logo_url(self, logo) -> str:
        """Return cached logo URL instead of calculated one which is slower."""
        return f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_BUCKET_NAME}/{logo.path_logo.name}"

    class Meta:
        model = Logo
        fields = "__all__"
