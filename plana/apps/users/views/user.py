from django.utils.translation import gettext_lazy as _

from dj_rest_auth.views import UserDetailsView as DJRestAuthUserDetailsView
from drf_spectacular.utils import extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, IsAuthenticated

from plana.apps.users.models.user import User
from plana.apps.users.serializers.user import UserSerializer


class UserList(generics.ListAPIView):
    serializer_class = UserSerializer
    queryset = User.objects.all().order_by("id")
    permission_classes = [IsAuthenticated]

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

    def get_permissions(self):
        if self.request.method == "PUT":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super(UserDetail, self).get_permissions()

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

    def patch(self, request, *args, **kwargs):
        if request.user.is_student:
            return response.Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )
        else:
            user = User.objects.get(id=kwargs["pk"])
            if user.get_cas_user():
                for restricted_field in [
                    "username",
                    "email",
                    "first_name",
                    "last_name",
                ]:
                    request.data.pop(restricted_field, False)
            return self.partial_update(request, *args, **kwargs)


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
