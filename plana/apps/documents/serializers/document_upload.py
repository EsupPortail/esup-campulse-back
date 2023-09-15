"""Serializers describing fields used on documents-association-user relations."""
from django.urls import reverse
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.users.models.user import User


class DocumentUploadSerializer(serializers.ModelSerializer):
    """Main serializer."""

    path_file = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_path_file(self, document):
        """Return a link to DocumentUploadFileRetrieve view."""
        return reverse('document_upload_file_retrieve', args=[document.id])

    @extend_schema_field(OpenApiTypes.INT)
    def get_size(self, document):
        """Return file size."""
        if document.path_file:
            return document.path_file.size
        else:
            return 0

    class Meta:
        model = DocumentUpload
        fields = "__all__"


class DocumentUploadCreateSerializer(serializers.ModelSerializer):
    """Main serializer not overriding path_file."""

    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all(), required=False)

    class Meta:
        model = DocumentUpload
        fields = [
            "id",
            "name",
            "document",
            "user",
            "association",
            "project",
            "validated_date",
            "path_file",
        ]


class DocumentUploadUpdateSerializer(serializers.ModelSerializer):
    """Serializer to validate a document."""

    class Meta:
        model = DocumentUpload
        fields = ["validated_date", "comment"]


class DocumentUploadFileSerializer(serializers.ModelSerializer):
    """Retrieve only the file itself."""

    class Meta:
        model = DocumentUpload
        fields = ["path_file", "name"]
