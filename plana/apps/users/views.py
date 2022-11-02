import requests
from allauth_cas.views import CASCallbackView, CASLoginView
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LogoutView
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics, status

from .adapter import CASAdapter
from .cas_serializer import CASSerializer
from .models import User
from .serializers import UserSerializer


class UserList(generics.ListCreateAPIView):
    """
    Generic DRF view to list associations or create a new one
    GET: list
    POST: create
    """
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all().order_by('username')


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET a single association (pk)
    """
    serializer_class = UserSerializer
    queryset = User.objects.all()

# login = CASLoginView.adapter_view(CASAdapter)
# callback = CASCallbackView.adapter_view(CASAdapter)


class CASLogin(SocialLoginView):
    adapter_class = CASAdapter
    serializer_class = CASSerializer


class CASLogout(LogoutView):
    # The user should be redirected to CASClient.get_logout_url(redirect_url=redirect_url)
    ...


def cas_test(request):
    service_url = reverse("cas_verify")
    service_url = urlencode({"service": request.build_absolute_uri(service_url)})
    redirect_url = f"{settings.CAS_SERVER}login?{service_url}"
    return HttpResponseRedirect(redirect_to=redirect_url)


def cas_verify(request):
    service_url = request.build_absolute_uri(reverse("cas_verify"))
    ticket = request.GET.get("ticket")

    response = requests.post(
        request.build_absolute_uri(reverse("rest_cas_login")),
        json={
            "service": service_url,
            "ticket": ticket,
        },
        headers={
            "Accept": "application/json",
        },
    )
    if response.ok:
        return JsonResponse({"token": response.json()["key"]})
    else:
        print(response)
