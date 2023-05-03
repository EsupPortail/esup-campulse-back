"""Serializers describing fields used on documents."""
from rest_framework import serializers

from plana.apps.documents.models.document import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Document
        fields = "__all__"


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for document create."""

    class Meta:
        model = Document
        fields = [
            "name",
            "description",
            "path_template",
            "mime_types",
            "institution",
            "commission",
        ]


class DocumentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for document update."""

    class Meta:
        model = Document
        fields = [
            "name",
            "description",
            "path_template",
            "mime_types",
        ]
