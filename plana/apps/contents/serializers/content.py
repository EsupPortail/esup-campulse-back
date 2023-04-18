"""Serializers describing fields used on contents."""
from rest_framework import serializers

from plana.apps.contents.models.content import Content


class ContentSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Content
        fields = "__all__"


class ContentBodySerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Content
        fields = ["body"]
