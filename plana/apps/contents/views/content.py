"""Views directly linked to contents."""
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.contents.models.content import Content
from plana.apps.contents.serializers.content import (
    ContentBodySerializer,
    ContentSerializer,
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

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "code",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Content code.",
            )
        ],
        responses={
            status.HTTP_200_OK: ContentSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists all contents."""
        return self.list(request, *args, **kwargs)


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

    @extend_schema(
        responses={
            status.HTTP_200_OK: ContentSerializer,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieves a content."""
        try:
            content_id = kwargs["pk"]
            Content.objects.get(id=content_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Content does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(
        exclude=True,
        responses={
            status.HTTP_405_METHOD_NOT_ALLOWED: None,
        },
    )
    def put(self, request, *args, **kwargs):
        return response.Response({}, status=status.HTTP_405_METHOD_NOT_ALLOWED)

    @extend_schema(
        responses={
            status.HTTP_200_OK: ContentBodySerializer,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        """Updates content details (manager only)."""
        try:
            content_id = kwargs["pk"]
            Content.objects.get(id=content_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Content does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )
        return self.partial_update(request, *args, **kwargs)
