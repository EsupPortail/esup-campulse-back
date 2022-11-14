from django.urls import include, path

# from rest_framework import routers
from . import views

# router = routers.DefaultRouter()
# router.register(r'associations', views.AssociationView)

urlpatterns = [
    path("", views.AssociationList.as_view(), name="association_list"),
    path("<int:pk>", views.AssociationDetail.as_view(), name="association_detail"),
]
