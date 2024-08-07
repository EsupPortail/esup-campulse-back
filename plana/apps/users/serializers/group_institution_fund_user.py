"""Serializers describing fields used on links between users and auth groups."""

from django.contrib.auth.models import Group
from rest_framework import serializers

from plana.apps.commissions.models.fund import Fund
from plana.apps.institutions.models.institution import Institution
from plana.apps.users.models.user import GroupInstitutionFundUser, User


class GroupInstitutionFundUserSerializer(serializers.ModelSerializer):
    """Main serializer."""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(), allow_null=True, required=False
    )
    fund = serializers.PrimaryKeyRelatedField(queryset=Fund.objects.all(), allow_null=True, required=False)

    class Meta:
        model = GroupInstitutionFundUser
        fields = "__all__"


class GroupInstitutionFundUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user-groups creation (with username instead of id)."""

    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())
    group = serializers.PrimaryKeyRelatedField(queryset=Group.objects.all())
    institution = serializers.PrimaryKeyRelatedField(
        queryset=Institution.objects.all(), allow_null=True, required=False
    )
    fund = serializers.PrimaryKeyRelatedField(queryset=Fund.objects.all(), allow_null=True, required=False)

    class Meta:
        model = GroupInstitutionFundUser
        fields = ["user", "group", "institution", "fund"]
