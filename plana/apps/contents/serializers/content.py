"""Serializers describing fields used on contents."""

from rest_framework import serializers

from plana.apps.contents.models.content import Content


class ContentSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Content
        fields = "__all__"


class ContentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for fields that can be updated as manager."""

    header = serializers.CharField(required=False, allow_blank=True)
    body = serializers.CharField(required=False, allow_blank=True)
    footer = serializers.CharField(required=False, allow_blank=True)
    aside = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Content
        fields = [
            "header",
            "body",
            "footer",
            "aside",
        ]
