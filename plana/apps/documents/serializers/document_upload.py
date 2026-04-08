"""Serializers describing fields used on documents-association-user relations."""

import datetime

from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from plana.apps.documents.models import Document
from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.users.models.user import User


class DocumentUploadListSerializer(serializers.ModelSerializer):
    """Main serializer without file size."""

    path_file = serializers.SerializerMethodField()
    calculated_expiration_date = serializers.ReadOnlyField()

    def get_path_file(self, document) -> str:
        """Return a link to DocumentUploadFileRetrieve view."""
        return reverse('document_upload_file_retrieve', args=[document.id])

    class Meta:
        model = DocumentUpload
        fields = "__all__"


class DocumentUploadRetrieveSerializer(serializers.ModelSerializer):
    """Main serializer with file size."""

    path_file = serializers.SerializerMethodField()
    size = serializers.SerializerMethodField()
    calculated_expiration_date = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.STR)
    def get_calculated_expiration_date(self, document):
        """Return real expiration date based on expiration_day or days_before_expiration."""
        if document.validated_date:
            if document.document.expiration_day:
                if document.document.expiration_day <= document.validated_date.strftime("%m-%d"):
                    return datetime.datetime.strptime(
                        f"{document.validated_date.year + 1}-{document.document.expiration_day}", "%Y-%m-%d"
                    )
                return datetime.datetime.strptime(
                    f"{document.validated_date.year}-{document.document.expiration_day}", "%Y-%m-%d"
                )
            if document.document.days_before_expiration:
                return document.validated_date + datetime.timedelta(days=document.document.days_before_expiration)
        return None

    @extend_schema_field(OpenApiTypes.STR)
    def get_path_file(self, document):
        """Return a link to DocumentUploadFileRetrieve view."""
        return reverse('document_upload_file_retrieve', args=[document.id])

    @extend_schema_field(OpenApiTypes.INT)
    def get_size(self, document):
        """Return file size."""
        if document.path_file:
            return document.path_file.size
        return 0

    class Meta:
        model = DocumentUpload
        fields = "__all__"


class DocumentUploadCreateSerializer(serializers.ModelSerializer):
    """Main serializer not overriding path_file."""

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


class DocumentUploadRegistrationCreateSerializer(serializers.ModelSerializer):
    """Serializer for DocumentUpload registration route."""

    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all(), required=True)

    def validate(self, attrs):
        document = attrs.get("document")
        user = attrs.get("user")
        if document.process_type not in Document.ProcessType.get_registration_documents():
            raise serializers.ValidationError(
                {"document_process": _("Provided document type must be linked to a registration process.")}
            )
        if DocumentUpload.objects.filter(document=document, user=user).count() >= document.max_uploads:
            raise serializers.ValidationError(
                {"max_uploads": _("Maximum number of uploads reached for this type of document.")}
            )
        return super().validate(attrs)

    class Meta:
        model = DocumentUpload
        fields = [
            "id",
            "name",
            "document",
            "user",
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
