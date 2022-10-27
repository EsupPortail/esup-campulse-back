from allauth_cas.urls import default_urlpatterns
from django.urls import path

from . import views
from .provider import CASProvider

urlpatterns = [
    path('<int:pk>', views.UserView.as_view(), name='user_by_id'),
    path('', views.UserView.as_view(), name='users'),
    #path('', views.index, name='index'),
]

urlpatterns += default_urlpatterns(CASProvider)
