"""Serializers describing fields used on links between users and auth groups."""
from django.contrib.auth.models import Group
from rest_framework import serializers

from plana.apps.commissions.models.fund import Fund
from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import GroupInstitutionCommissionUser, User


class GroupInstitutionCommissionUserSerializer(serializers.ModelSerializer):
    """Main serializer."""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(), allow_null=True, required=False
    )
    commission = serializers.PrimaryKeyRelatedField(
        queryset=Fund.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = GroupInstitutionCommissionUser
        fields = "__all__"


class GroupInstitutionCommissionUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user-groups creation (with username instead of id)."""

    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(), allow_null=True, required=False
    )
    commission = serializers.PrimaryKeyRelatedField(
        queryset=Fund.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = GroupInstitutionCommissionUser
        fields = ["user", "group", "institution", "commission"]
