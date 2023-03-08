"""Views directly linked to documents."""
from rest_framework import generics

from plana.apps.documents.models.document import Document
from plana.apps.documents.serializers.document import DocumentSerializer


class DocumentList(generics.ListAPIView):
    """Lists all Documents."""

    serializer_class = DocumentSerializer

    def get_queryset(self):
        """GET : Lists all documents."""
        return Document.objects.all()
