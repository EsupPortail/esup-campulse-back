"""Serializers describing fields used on links between users and auth groups."""
from django.contrib.auth.models import Group
from rest_framework import serializers

from plana.apps.commissions.models.commission import Commission
from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import GroupInstitutionCommissionUsers, User


class UserGroupsInstitutionsCommissionsSerializer(serializers.ModelSerializer):
    """Main serializer."""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(), allow_null=True, required=False
    )
    commission = serializers.PrimaryKeyRelatedField(
        queryset=Commission.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = GroupInstitutionCommissionUsers
        fields = "__all__"


class UserGroupsInstitutionsCommissionsCreateSerializer(serializers.ModelSerializer):
    """Serializer for user-groups creation (with username instead of id)."""

    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(), allow_null=True, required=False
    )
    commission = serializers.PrimaryKeyRelatedField(
        queryset=Commission.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = GroupInstitutionCommissionUsers
        fields = ["user", "group", "institution", "commission"]
