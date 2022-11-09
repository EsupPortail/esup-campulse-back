import requests
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LogoutView
from django.conf import settings
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import generics, response, status

from .adapter import CASAdapter
from .models import User
from .serializers.cas import CASSerializer
from .serializers.user import UserSerializer


class UserList(generics.ListCreateAPIView):
    """
    Generic DRF view to list users or create a new one
    GET: list
    POST: create
    """

    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.all().order_by("username")


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """
    GET a single user (pk)
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(instance=user)
        return response.Response(serializer.data)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(instance=request.user, data=request.data, partial=True)
        if serializer.is_valid(raise_exception=True):
            if serializer.instance.get_cas_user():
                print(serializer.instance.get_cas_user().extra_data)
            # TODO : Check if user authenticated with CAS cannot PATCH the fields auto-filled by CAS (not testable on localhost because CAS-dev doesn't allow it).
            """
            if serializer.instance.get_cas_user():
                cas_user_response = serializer.instance.get_cas_user()
                cas_restricted_fields = CASAdapter.get_provider().extract_common_fields(cas_user_response)
                print(cas_user_response.extra_data)
            """
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)



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
        return JsonResponse(response.json())
    else:
        print(response)
