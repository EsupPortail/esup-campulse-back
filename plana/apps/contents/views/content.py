"""Views directly linked to contents."""
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.contents.models.content import Content
from plana.apps.contents.serializers.content import (
    ContentBodySerializer,
    ContentSerializer,
)


@extend_schema_view(
    get=extend_schema(
        parameters=[
            OpenApiParameter(
                "code",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Content code.",
            )
        ]
    )
)
class ContentList(generics.ListAPIView):
    """/contents/ route"""

    permission_classes = [AllowAny]
    serializer_class = ContentSerializer

    def get_queryset(self):
        queryset = Content.objects.all()
        code = self.request.query_params.get("code")
        if code is not None and code != "":
            queryset = queryset.filter(code=code)
        return queryset

    def get(self, request, *args, **kwargs):
        """Lists all contents."""
        return self.list(request, *args, **kwargs)


@extend_schema(methods=["PUT"], exclude=True)
# TODO : unittests
class ContentRetrieveUpdate(generics.RetrieveUpdateAPIView):
    queryset = Content.objects.all()

    def get_permissions(self):
        if self.request.method == "PATCH":
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        else:
            self.permission_classes = [AllowAny]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = ContentSerializer
        else:
            self.serializer_class = ContentBodySerializer
        return super().get_serializer_class()

    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
