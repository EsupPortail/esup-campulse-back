from django.urls import include, path
from . import views

urlpatterns = [
    path('<int:pk>', views.UserView.as_view(), name='user_by_id'),
    path('', views.UserView.as_view(), name='users'),
    #path('', views.index, name='index'),
]
