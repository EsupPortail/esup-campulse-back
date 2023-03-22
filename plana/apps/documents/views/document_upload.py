"""Views directly linked to document uploads."""
from rest_framework import generics, response, status
from rest_framework.permissions import IsAuthenticated

from plana.apps.documents.models.document_upload import DocumentUpload
from plana.apps.documents.serializers.document_upload import DocumentUploadSerializer


class DocumentUploadList(generics.ListAPIView):
    """
    GET : Lists all DocumentUploads.
    """

    serializer_class = DocumentUploadSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """GET : Lists all document uploads."""
        return DocumentUpload.objects.all()
