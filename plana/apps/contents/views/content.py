"""Views directly linked to contents."""

from rest_framework import generics
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.contents.models.content import Content
from plana.apps.contents.serializers.content import (
    ContentSerializer,
    ContentUpdateSerializer,
)
from .. import filters


class ContentList(generics.ListAPIView):
    """/contents/ route."""

    permission_classes = [AllowAny]
    queryset = Content.objects.all().order_by("id")
    serializer_class = ContentSerializer
    filterset_class = filters.ContentFilter


class ContentRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """/contents/{id} route."""

    queryset = Content.objects.all()
    http_method_names = ["get", "patch"]

    def get_permissions(self):
        if self.request.method == "GET":
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated, DjangoModelPermissions]
        return super().get_permissions()

    def get_serializer_class(self):
        if self.request.method == "GET":
            self.serializer_class = ContentSerializer
        else:
            self.serializer_class = ContentUpdateSerializer
        return super().get_serializer_class()
