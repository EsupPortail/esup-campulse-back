import requests

from rest_framework import generics, response, status
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LogoutView

from django.conf import settings
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.utils.http import urlencode
from django.utils.translation import gettext_lazy as _

from plana.apps.users.adapter import CASAdapter
from plana.apps.users.models.user import User, AssociationUsers
from plana.apps.users.serializers.cas import CASSerializer
from plana.apps.users.serializers.user import (
    UserSerializer,
    AssociationUsersSerializer,
)

###########
#  Users  #
###########

"""
class UserList(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by("username")

    @extend_schema(
        responses={ 201: UserSerializer, 401: None },
    )
    def post(self, request, *args, **kwargs):
        request.data["username"] = request.data["email"]
        return self.create(request, *args, **kwargs)


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(instance=user)
        try:
            return response.Response(serializer.data)
        except AttributeError:
            return response.Response({}, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            instance=request.user, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            if serializer.instance.get_cas_user():
                print(serializer.instance.get_cas_user().extra_data)
            # TODO : Check if user authenticated with CAS cannot PATCH the fields auto-filled by CAS (not testable on localhost because CAS-dev doesn't allow it).
            # if serializer.instance.get_cas_user():
            #    cas_user_response = serializer.instance.get_cas_user()
            #    cas_restricted_fields = CASAdapter.get_provider().extract_common_fields(cas_user_response)
            #    print(cas_user_response.extra_data)
            serializer.save()
            return response.Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return response.Response({}, status=status.HTTP_400_BAD_REQUEST)
"""


##################
#  Associations  #
##################


# TODO Only work if authenticated user is username in request, and not validated by admin.


class UserAssociationsCreate(generics.CreateAPIView):
    """
    POST : Creates a new link between an user and an association.
    """

    serializer_class = AssociationUsersSerializer
    queryset = AssociationUsers.objects.all()


class UserAssociationsList(generics.RetrieveDestroyAPIView):
    """
    GET : Lists all associations linked to an user.
    DELETE : Deletes a link between an association and a user.
    """

    serializer_class = AssociationUsersSerializer
    queryset = AssociationUsers.objects.all()

    def get(self, request, *args, **kwargs):
        associations_user = AssociationUsers.objects.get(user_id=request.user.pk)
        serializer = self.serializer_class(instance=associations_user)
        return response.Response(serializer.data)


#########
#  CAS  #
#########


class CASLogin(SocialLoginView):
    """
    POST : Authenticates an user through CAS with django-allauth-cas and dj-rest-auth.
    """

    adapter_class = CASAdapter
    serializer_class = CASSerializer


class CASLogout(LogoutView):
    """
    GET : Logs out an user authenticated with CAS out.
    POST : Logs out an user authenticated with CAS out.
    """

    adapter_class = CASAdapter
    serializer_class = CASSerializer

    # The user should be redirected to CASClient.get_logout_url(redirect_url=redirect_url)
    ...


##################
#  dj-rest-auth  #
##################


class PasswordResetConfirm(generics.GenericAPIView):
    """
    POST : Blank redirection to make the password reset work (see https://dj-rest-auth.readthedocs.io/en/latest/faq.html ).
    """

    ...


############
#  Groups  #
############


# TODO Only work if authenticated user is username in request, and not validated by admin.


class UserGroupsCreate(generics.CreateAPIView):
    """
    POST : Creates a new link between an user and a group.
    """

    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            instance=request.user, data=request.data, partial=True
        )
        if serializer.is_valid(raise_exception=True):
            """
            TODO : restrict the route if is_validated_by_admin is set to true.
            """
            user = User.objects.get(email=request.data["user"])
            for id_group in request.data["groups"]:
                group = Group.objects.get(id=id_group)
                user.groups.add(group)
            return response.Response({}, status=status.HTTP_200_OK)
        else:
            return response.Response({}, status=status.HTTP_400_BAD_REQUEST)


class UserGroupsList(generics.RetrieveDestroyAPIView):
    """
    GET : Lists all groups linked to an user.
    DELETE : Deletes a link between a group and a user.
    """

    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        user = request.user
        serializer = self.serializer_class(instance=user)
        return response.Response(serializer.data["groups"])


###############
#  CAS Debug  #
###############


# login = CASLoginView.adapter_view(CASAdapter)
# callback = CASCallbackView.adapter_view(CASAdapter)


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