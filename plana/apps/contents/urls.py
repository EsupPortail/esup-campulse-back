"""List of URLs directly linked to operations that can be done on contents."""

from django.urls import path

from .views.content import ContentList, ContentRetrieveUpdate
from .views.logo import LogoList

urlpatterns = [
    path("", ContentList.as_view(), name="content_list"),
    path("<int:pk>", ContentRetrieveUpdate.as_view(), name="content_retrieve_update"),
    path("logos", LogoList.as_view(), name="logo_list"),
]
