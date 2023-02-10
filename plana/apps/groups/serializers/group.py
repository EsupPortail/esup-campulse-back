"""
Serializers describing fields used on auth groups.
"""
from django.contrib.auth.models import Group
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    permissions = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_permissions(self, group):
        """
        Return permissions links.
        """
        return Group.objects.get(id=group.id).permissions.values_list(
            'codename', flat=True
        )

    class Meta:
        model = Group
        fields = ("id", "name", "permissions")
