"""Serializers describing fields used on documents."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from plana.apps.documents.models.document import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Main serializer."""

    size = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.INT)
    def get_size(self, document):
        """Return file size."""
        if document.path_template:
            return document.path_template.size
        return 0

    class Meta:
        model = Document
        fields = "__all__"


class DocumentCreateSerializer(serializers.ModelSerializer):
    """Serializer for document create."""

    class Meta:
        model = Document
        fields = [
            "id",
            "name",
            "description",
            "path_template",
            "institution",
            "fund",
        ]


class DocumentUpdateSerializer(serializers.ModelSerializer):
    """Serializer for document update."""

    class Meta:
        model = Document
        fields = [
            "name",
            "description",
            "path_template",
        ]
