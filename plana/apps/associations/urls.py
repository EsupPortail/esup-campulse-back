from django.urls import path

from .views.association import AssociationList, AssociationDetail


urlpatterns = [
    path("", AssociationList.as_view(), name="association_list"),
    path("<int:pk>", AssociationDetail.as_view(), name="association_detail"),
]
