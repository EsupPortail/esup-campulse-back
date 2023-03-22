"""Serializers describing fields used on documents-association-user relations."""
from rest_framework import serializers

from plana.apps.documents.models.document_upload import DocumentUpload


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Main serializer."""

    class Meta:
        model = DocumentUpload
        fields = "__all__"
