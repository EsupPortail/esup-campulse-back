from allauth_cas.urls import default_urlpatterns
from django.urls import path

from . import views
from .provider import CASProvider

urlpatterns = [
    path('<int:pk>', views.UserDetail.as_view(), name='user_detail'),
    path('', views.UserList.as_view(), name='user_list'),
    path("djcas/login/", views.CASLogin.as_view(), name="rest_cas_login"),
    #path('', views.index, name='index'),

    path("cas_test/", views.cas_test, name="cas_test"),
    path("cas_verify/", views.cas_verify, name="cas_verify"),
]

urlpatterns += default_urlpatterns(CASProvider)
