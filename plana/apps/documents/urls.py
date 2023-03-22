"""List of URLs directly linked to operations that can be done on documents."""
from django.urls import path

from .views.document import DocumentList, DocumentRetrieveDestroy
from .views.document_upload import DocumentUploadList

urlpatterns = [
    # Documents types urls
    path("", DocumentList.as_view(), name="document_list"),
    path(
        "<int:pk>", DocumentRetrieveDestroy.as_view(), name="document_retrieve_destroy"
    ),
    # Document uploads urls
    path(
        "uploads",
        DocumentUploadList.as_view(),
        name="document_upload_list",
    ),
]
