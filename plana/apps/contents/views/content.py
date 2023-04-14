"""Views directly linked to contents."""
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema, extend_schema_view
from rest_framework import generics
from rest_framework.permissions import AllowAny

from plana.apps.contents.models.content import Content
from plana.apps.contents.serializers.content import ContentSerializer


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
