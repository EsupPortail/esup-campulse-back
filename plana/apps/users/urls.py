from allauth_cas.urls import default_urlpatterns
from django.urls import path

from . import views
from .provider import CASProvider

urlpatterns = [
    path('<int:pk>', views.UserDetail.as_view(), name='user_detail'),
    path('', views.UserList.as_view(), name='user_list'),
    #path('', views.index, name='index'),
]

urlpatterns += default_urlpatterns(CASProvider)
