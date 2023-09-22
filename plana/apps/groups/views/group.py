"""Views directly linked to auth groups."""
from django.contrib.auth.models import Group
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from plana.apps.groups.serializers.group import GroupSerializer


class GroupList(generics.ListAPIView):
    """/groups/ route."""

    permission_classes = [AllowAny]
    queryset = Group.objects.all().order_by("name")
    serializer_class = GroupSerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                "name",
                OpenApiTypes.STR,
                OpenApiParameter.QUERY,
                description="Group name.",
            )
        ],
        responses={
            status.HTTP_200_OK: GroupSerializer,
        },
    )
    def get(self, request, *args, **kwargs):
        """List all groups."""
        name = request.query_params.get("name")

        if name is not None and name != "":
            self.queryset = self.queryset.filter(name=name)

        return self.list(request, *args, **kwargs)
