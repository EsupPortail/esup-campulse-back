"""
List of URLs directly linked to operations that can be done on associations.
"""
from django.urls import path

from .views.association import AssociationListCreate, AssociationRetrieveUpdateDestroy

urlpatterns = [
    path("", AssociationListCreate.as_view(), name="association_list_create"),
    path(
        "<int:pk>",
        AssociationRetrieveUpdateDestroy.as_view(),
        name="association_retrieve_update_destroy",
    ),
]
