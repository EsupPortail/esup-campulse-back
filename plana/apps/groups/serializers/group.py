"""
Serializers describing fields used on auth groups.
"""
from django.conf import settings
from django.contrib.auth.models import Group
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers


class GroupSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    permissions = serializers.SerializerMethodField()
    is_public = serializers.SerializerMethodField("is_public_group")

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_permissions(self, group):
        """
        Return permissions links.
        """
        return group.permissions.values_list("codename", flat=True)

    def is_public_group(self, group) -> bool:
        """
        True if the group can be selected on normal registration.
        """
        return group.name in settings.PUBLIC_GROUPS

    class Meta:
        model = Group
        fields = ("id", "name", "permissions", "is_public")
