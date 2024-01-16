"""Views directly linked to contents."""
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, DjangoModelPermissions, IsAuthenticated

from plana.apps.contents.models.content import Content
from plana.apps.contents.serializers.content import (
    ContentSerializer,
    ContentUpdateSerializer,
)
from plana.utils import to_bool


class ContentList(generics.ListAPIView):
    """/contents/ route."""

    permission_classes = [AllowAny]
    queryset = Content.objects.all()
    serializer_class = ContentSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "code",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Content code.",
            ),
            OpenApiParameter(
                "is_editable",
                OpenApiTypes.BOOL,
                OpenApiParameter.QUERY,
                description="Is editable.",
            ),
        ],
        responses={
            status.HTTP_200_OK: ContentSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """List all contents."""
        code = request.query_params.get("code")
        is_editable = request.query_params.get("is_editable")

        if code is not None and code != "":
            self.queryset = self.queryset.filter(code=code)

        if is_editable is not None and is_editable != "":
            self.queryset = self.queryset.filter(is_editable=to_bool(is_editable))

        return self.list(request, *args, **kwargs)


class ContentRetrieveUpdate(generics.RetrieveUpdateAPIView):
    """/contents/{id} route."""

    queryset = Content.objects.all()

    def get_permissions(self):
        if self.request.method in ("GET", "PUT"):
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

    @extend_schema(
        responses={
            status.HTTP_200_OK: ContentSerializer,
            status.HTTP_404_NOT_FOUND: None,
        },
    )
    def get(self, request, *args, **kwargs):
        """Retrieve a content."""
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
            status.HTTP_200_OK: ContentUpdateSerializer,
            status.HTTP_400_BAD_REQUEST: None,
            status.HTTP_401_UNAUTHORIZED: None,
            status.HTTP_403_FORBIDDEN: None,
            status.HTTP_404_NOT_FOUND: None,
        }
    )
    def patch(self, request, *args, **kwargs):
        """Update association details (president and manager only, restricted fields for president)."""
        try:
            content_id = kwargs["pk"]
            content = Content.objects.get(id=content_id)
        except ObjectDoesNotExist:
            return response.Response(
                {"error": _("Content does not exist.")},
                status=status.HTTP_404_NOT_FOUND,
            )

        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
        except ValidationError as error:
            return response.Response(
                {"error": error.detail},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not request.user.has_perm("contents.change_content"):
            return response.Response(
                {"error": _("Not allowed to edit this content.")},
                status=status.HTTP_403_FORBIDDEN,
            )

        if content.is_editable is False:
            return response.Response(
                {"error": _("This content is not editable.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return self.partial_update(request, *args, **kwargs)
