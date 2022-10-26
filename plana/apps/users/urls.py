from django.urls import include, path
from . import views

urlpatterns = [
    path('', views.UserView.as_view(), name='users'),
    #path('', views.index, name='index'),
]
