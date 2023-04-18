"""List of URLs directly linked to operations that can be done on contents."""
from django.urls import path

from .views.content import ContentList, ContentRetrieveUpdate

urlpatterns = [
    path("", ContentList.as_view(), name="content_list"),
    path("<int:pk>", ContentRetrieveUpdate.as_view(), name="content_retrieve_update"),
]
