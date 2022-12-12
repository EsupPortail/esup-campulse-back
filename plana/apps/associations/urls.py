"""
List of URLs directly linked to operations that can be done on associations.
"""
from django.urls import path

from .views.association import AssociationListCreate, AssociationRetrieveDestroy

urlpatterns = [
    path("", AssociationListCreate.as_view(), name="association_list_create"),
    path(
        "<int:pk>",
        AssociationRetrieveDestroy.as_view(),
        name="association_retrieve_destroy",
    ),
]
