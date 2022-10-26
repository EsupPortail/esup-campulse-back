from django.urls import include, path
#from rest_framework import routers
from . import views

#router = routers.DefaultRouter()
#router.register(r'associations', views.AssociationView)

urlpatterns = [
    #path('', include(router.urls)),
    path('', views.AssociationView.as_view(), name='associations'),
]
