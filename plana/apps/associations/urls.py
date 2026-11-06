"""List of URLs directly linked to operations that can be done on associations."""

from django.urls import path

from .views.activity_field import AssociationActivityFieldList
from .views.association import (
    AssociationNameList,
    AssociationStatusUpdate, AssociationMembersView, AssociationManageListCreate, AssociationRetrieve,
    AssociationManageRetrieveUpdateDestroy, AssociationList,
)
from .views.association_export import AssociationListExport, AssociationRetrieveExport

urlpatterns = [
    path("", AssociationList.as_view(), name="association_list"),
    path("<int:pk>", AssociationRetrieve.as_view(), name="association_retrieve"),
    path("manage", AssociationManageListCreate.as_view(), name="association_manage_list_create"),
    path(
        "<int:pk>/manage",
        AssociationManageRetrieveUpdateDestroy.as_view(),
        name="association_manage_retrieve_update_destroy",
    ),
    path(
        "<int:pk>/export",
        AssociationRetrieveExport.as_view(),
        name="association_retrieve_export",
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
        "export",
        AssociationListExport.as_view(),
        name="associations_list_export",
    ),
    path("names", AssociationNameList.as_view(), name="association_name_list"),
    path("<int:association_id>/users", AssociationMembersView.as_view(), name="association_user_links"),
]
