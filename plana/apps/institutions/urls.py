"""List of URLs directly linked to operations that can be done on associations."""
from django.urls import path

from .views.institution import InstitutionList
from .views.institution_component import InstitutionComponentList

urlpatterns = [
    path(
        "",
        InstitutionList.as_view(),
        name="association_institution_list",
    ),
    path(
        "institution_components",
        InstitutionComponentList.as_view(),
        name="association_institution_component_list",
    ),
]
