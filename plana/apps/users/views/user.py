from django.utils.translation import gettext_lazy as _

from dj_rest_auth.views import UserDetailsView as DJRestAuthUserDetailsView
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status

from plana.apps.users.models.user import User
from plana.apps.users.serializers.user import UserSerializer


class UserList(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by("username")

    def get(self, request, *args, **kwargs):
        if request.user.is_student:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            return self.list(request, *args, **kwargs)


@extend_schema(methods=["PUT"], exclude=True)
class UserDetail(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all()

    def get(self, request, *args, **kwargs):
        if request.user.is_student:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            return self.retrieve(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_404_NOT_FOUND)

    """
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


class PasswordResetConfirm(generics.GenericAPIView):
    """
    POST : Blank redirection to make the password reset work (see https://dj-rest-auth.readthedocs.io/en/latest/faq.html ).
    """

    ...


@extend_schema(methods=["PUT"], exclude=True)
class UserDetailsView(DJRestAuthUserDetailsView):
    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_404_NOT_FOUND)

    def patch(self, request, *args, **kwargs):
        request.data.pop("is_validated_by_admin", False)
        if request.user.get_cas_user():
            for restricted_field in ["username", "email", "first_name", "last_name"]:
                request.data.pop(restricted_field, False)
        return self.partial_update(request, *args, **kwargs)
