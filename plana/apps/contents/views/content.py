"""Views directly linked to contents."""
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, response, status
from rest_framework.permissions import AllowAny

from plana.apps.contents.models.content import Content
from plana.apps.contents.serializers.content import ContentSerializer


class ContentList(generics.ListAPIView):
    """/contents/ route"""

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
            )
        ],
        responses={
            status.HTTP_200_OK: ContentSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """Lists all contents."""
        code = request.query_params.get("code")

        if code is not None and code != "":
            self.queryset = self.queryset.filter(code=code)

        return self.list(request, *args, **kwargs)


class ContentRetrieve(generics.RetrieveAPIView):
    """/contents/{id} route"""

    permission_classes = [AllowAny]
    queryset = Content.objects.all()
    serializer_class = ContentSerializer

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
