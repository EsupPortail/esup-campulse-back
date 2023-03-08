"""List of URLs directly linked to operations that can be done on documents."""
from django.urls import path

from .views.document import DocumentList

urlpatterns = [
    path("", DocumentList.as_view(), name="document_list"),
]
