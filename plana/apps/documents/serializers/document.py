"""Serializers describing fields used on documents."""
from rest_framework import serializers

from plana.apps.documents.models.document import Document


class DocumentSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = Document
        fields = "__all__"
