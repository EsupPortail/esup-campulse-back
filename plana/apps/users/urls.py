from django.conf import settings
from django.urls import include, path

from . import views

urlpatterns = [
    path("<int:pk>", views.UserDetail.as_view(), name="user_detail"),
    path("", views.UserDetail.as_view(), name="user_list"),
    # path('', views.index, name='index'),
    path("auth/cas/login/", views.CASLogin.as_view(), name="rest_cas_login"),
    path("auth/cas/logout/", views.CASLogout.as_view(), name="rest_cas_logout"),
    path("auth/", include("dj_rest_auth.urls")),
    path("auth/registration/", include("dj_rest_auth.registration.urls")),
]

if settings.DEBUG:
    urlpatterns += [
        path("auth/cas_test/", views.cas_test, name="cas_test"),
        path("auth/cas_verify/", views.cas_verify, name="cas_verify"),
    ]
