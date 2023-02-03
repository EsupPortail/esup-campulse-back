"""
List of URLs directly linked to operations that can be done on associations.
"""
from django.urls import path

from .views.institution import (
    AssociationInstitutionComponentList,
    AssociationInstitutionList,
)

urlpatterns = [
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
