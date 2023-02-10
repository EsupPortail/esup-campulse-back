"""
Serializers describing fields used on links between users and auth groups.
"""
from django.contrib.auth.models import Group
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import GroupInstitutionUsers, User


class UserGroupsInstitutionsSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = GroupInstitutionUsers
        fields = "__all__"
