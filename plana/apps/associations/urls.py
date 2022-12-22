"""
List of URLs directly linked to operations that can be done on associations.
"""
from django.urls import path

from .views.association import (
    AssociationActivityFieldList,
    AssociationInstitutionComponentList,
    AssociationInstitutionList,
    AssociationListCreate,
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
        "institution_components",
        AssociationInstitutionComponentList.as_view(),
        name="association_institution_component_list",
    ),
    path(
        "institutions",
        AssociationInstitutionList.as_view(),
        name="association_institution_list",
    ),
]
