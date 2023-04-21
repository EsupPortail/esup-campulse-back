"""Serializers describing fields used on documents-association-user relations."""
from django.urls import reverse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from plana.apps.documents.models.document_upload import DocumentUpload


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Main serializer."""

    path_file = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_path_file(self, document):
        """Return a link to DocumentUploadFileRetrieve view."""
        return reverse('document_upload_file_retrieve', args=[document.id])

    class Meta:
        model = DocumentUpload
        fields = "__all__"


class DocumentUploadCreateSerializer(serializers.ModelSerializer):
    """Main serializer not overriding path_file."""

    class Meta:
        model = DocumentUpload
        fields = "__all__"


class DocumentUploadFileSerializer(serializers.ModelSerializer):
    """Retrieve only the file itself."""

    class Meta:
        model = DocumentUpload
        fields = ["path_file", "name"]
