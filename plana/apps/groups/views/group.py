"""Views directly linked to auth groups."""
from django.contrib.auth.models import Group
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiParameter, extend_schema
from rest_framework import generics, status
from rest_framework.permissions import AllowAny

from plana.apps.groups.serializers.group import GroupSerializer


class GroupList(generics.ListAPIView):
    """/groups/ route"""

    permission_classes = [AllowAny]
    serializer_class = GroupSerializer

    def get_queryset(self):
        queryset = Group.objects.all().order_by("name")
        name = self.request.query_params.get("name")
        if name is not None and name != "":
            queryset = queryset.filter(name=name)
        return queryset

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
        """Lists all groups."""
        return self.list(request, *args, **kwargs)
