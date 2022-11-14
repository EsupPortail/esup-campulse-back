from django.urls import path

# from rest_framework import routers
from .views.association import AssociationList, AssociationDetail

# router = routers.DefaultRouter()
# router.register(r'associations', views.AssociationView)

urlpatterns = [
    path("", AssociationList.as_view(), name="association_list"),
    path("<int:pk>", AssociationDetail.as_view(), name="association_detail"),
]
