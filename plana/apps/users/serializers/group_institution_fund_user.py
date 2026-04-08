"""Serializers describing fields used on links between users and auth groups."""
from django.conf import settings
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from plana.apps.commissions.models.fund import Fund
from plana.apps.history.models import History
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
    """Serializer for user-groups creation."""

    institution = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all(), allow_null=True, required=False)
    fund = serializers.PrimaryKeyRelatedField(queryset=Fund.objects.all(), allow_null=True, required=False)

    class Meta:
        model = GroupInstitutionFundUser
        fields = "__all__"

    def validate(self, attrs):
        user, group, institution, fund = attrs.get("user"), attrs.get("group"), attrs.get("institution"), attrs.get("fund")
        auth_user = self.context["request"].user
        # Cannot link a user to the same gifu twice -> None value always considered different
        if (
            GroupInstitutionFundUser.objects.filter(
                user=user,
                group=attrs.get("group"),
                institution=attrs.get("institution"),
                fund=attrs.get("fund"),
            ).exists()
        ):
            raise serializers.ValidationError({"already_exists": _("Link between user and group already exists.")})

        group_structure = settings.GROUPS_STRUCTURE[group.name]
        # managers and superuser GIFU updates are forbidden through the API
        # TODO : Find a better way to define it
        if user.is_superuser or any(not settings.GROUPS_STRUCTURE[group.name]["REGISTRATION_ALLOWED"] for group in user.get_user_groups()):
            raise serializers.ValidationError({"rights_level": _("Groups for a manager cannot be changed.")})

        if not group_structure["REGISTRATION_ALLOWED"]:
            raise serializers.ValidationError({"restricted_group": _("Adding a user in a restricted group is not allowed.")})

        if institution:
            if not group_structure["INSTITUTION_ID_POSSIBLE"] or institution not in auth_user.get_user_managed_institutions():
                raise serializers.ValidationError({"institution": _("Adding institution in this group is not possible.")})

        if fund:
            if not group_structure["FUND_ID_POSSIBLE"] or fund.institution not in auth_user.get_user_managed_institutions():
                raise serializers.ValidationError({"fund": _("Adding fund in this group is not possible.")})

        return attrs

    def create(self, validated_data):
        instance = super().create(validated_data)
        History.objects.create(
            action_title="GROUP_INSTITUTION_FUND_USER_CHANGED",
            action_user=self.context["request"].user,
            group_institution_fund_user=instance,
        )
        return instance
