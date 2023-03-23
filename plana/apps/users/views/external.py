"""View interacting with LDAP API endpoint."""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from plana.libs.api.accounts import Client

from ..serializers.external import ExternalUserSerializer


class ExternalUserRetrieve(generics.ListAPIView):
    """
    GET : Retrieve an external user.
    """

    serializer_class = ExternalUserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "last_name",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        if not request.user.has_perm("users.add_user") and not request.user.has_perm(
            "users.add_user_misc"
        ):
            return Response(
                {"error": _("Bad request.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        try:
            if last_name := self.request.query_params.get("last_name"):
                data = Client().list_users(last_name=last_name)
                serializer = self.get_serializer(data, many=True)
                return Response(serializer.data)
            else:
                return Response(
                    {"error": _("No last name given.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
