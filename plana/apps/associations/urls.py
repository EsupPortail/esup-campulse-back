from django.urls import path

from .views.association import AssociationList, AssociationRetrieve


urlpatterns = [
    path("", AssociationList.as_view(), name="association_list"),
    path("<int:pk>", AssociationRetrieve.as_view(), name="association_retrieve"),
]
