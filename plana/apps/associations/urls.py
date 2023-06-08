"""List of URLs directly linked to operations that can be done on associations."""
from django.urls import path

from .views.activity_field import AssociationActivityFieldList
from .views.association import (
    AssociationListCreate,
    AssociationNameList,
    AssociationRetrieveUpdateDestroy,
)

urlpatterns = [
    path("", AssociationListCreate.as_view(), name="association_list_create"),
    path(
        "<int:pk>",
        AssociationRetrieveUpdateDestroy.as_view(),
        name="association_retrieve_update_destroy",
    ),
    path(
        "activity_fields",
        AssociationActivityFieldList.as_view(),
        name="association_activity_field_list",
    ),
    path(
        "names",
        AssociationNameList.as_view(),
        name="association_name_list",
    ),
]
