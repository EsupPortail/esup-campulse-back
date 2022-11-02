from django.urls import include, path
from . import views

urlpatterns = [
    path('<int:pk>', views.UserDetail.as_view(), name='user_detail'),
    path('', views.UserList.as_view(), name='user_list'),
    #path('', views.index, name='index'),
]
