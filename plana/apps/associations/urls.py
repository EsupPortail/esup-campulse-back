"""List of URLs directly linked to operations that can be done on associations."""
from django.urls import path

from .views.activity_field import AssociationActivityFieldList
from .views.association import (
    AssociationListCreate,
    AssociationNameList,
    AssociationRetrieveUpdateDestroy,
    AssociationStatusUpdate,
)
from .views.association_export import AssociationDataExport, AssociationsCSVExport

urlpatterns = [
    path("", AssociationListCreate.as_view(), name="association_list_create"),
    path(
        "<int:pk>",
        AssociationRetrieveUpdateDestroy.as_view(),
        name="association_retrieve_update_destroy",
    ),
    path(
        "<int:pk>/export",
        AssociationDataExport.as_view(),
        name="association_data_export",
    ),
    path(
        "<int:pk>/status",
        AssociationStatusUpdate.as_view(),
        name="association_status_update",
    ),
    path(
        "activity_fields",
        AssociationActivityFieldList.as_view(),
        name="association_activity_field_list",
    ),
    path(
        "csv_export",
        AssociationsCSVExport.as_view(),
        name="associations_csv_export",
    ),
    path("names", AssociationNameList.as_view(), name="association_name_list"),
]
