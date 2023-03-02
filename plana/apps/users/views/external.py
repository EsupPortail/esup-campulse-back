from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from django.http import Http404
from django.utils.translation import gettext_lazy as _

from plana.libs.api.accounts import Client
from ..serializers.external import ExternalUserSerializer


class ExternalUserRetrieve(generics.RetrieveAPIView):
    """
    GET : Retrieve an external user
    """

    serializer_class = ExternalUserSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "username",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                required=True,
            ),
        ]
    )
    def get(self, request, *args, **kwargs):
        try:
            if username := self.request.query_params.get("username"):
                if data := Client().get_user(username=username):
                    serializer = self.get_serializer(data)
                    return Response(serializer.data)
                else:
                    return Response(status=status.HTTP_404_NOT_FOUND)
            else:
                return Response(
                    {"error": _("No username given.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
