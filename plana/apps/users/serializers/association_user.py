"""Serializers describing fields used on links between users and associations."""
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import (
    AssociationMandatoryDataSerializer,
)
from plana.apps.institutions.models import Institution
from plana.apps.users.models.user import AssociationUser, User
from plana.apps.users.serializers.user import UserNameSerializer
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class AssociationUserSerializer(serializers.ModelSerializer):
    """Main serializer."""

    user = UserNameSerializer(read_only=True)
    association = AssociationMandatoryDataSerializer(read_only=True)

    class Meta:
        model = AssociationUser
        fields = "__all__"


class AssociationUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user-associations creation."""

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    association = serializers.PrimaryKeyRelatedField(queryset=Association.objects.all())

    class Meta:
        model = AssociationUser
        fields = [
            "user",
            "association",
            "is_president",
            "is_validated_by_admin",
            "is_vice_president",
            "is_secretary",
            "is_treasurer",
        ]
        read_only_fields = ["is_validated_by_admin"]

    # TODO : only one role in asso accepted ?
    def validate(self, data):
        association = data.get("association")
        user = data.get("user")
        auth_user = self.context["request"].user

        if not any(settings.GROUPS_STRUCTURE[group.name]["ASSOCIATIONS_POSSIBLE"] for group in user.get_user_groups()):
            raise serializers.ValidationError({"missing_group": _("The user hasn't any group that can have associations.")})

        if association.associationuser_set.count() >= association.amount_members_allowed:
            raise serializers.ValidationError({"too_many_members": _("Too many users in association.")})

        if data.get("is_president") and AssociationUser.objects.filter(association=association, is_president=True).exists():
            raise serializers.ValidationError({"president": _("President already in association.")})

        # If auth user manages given association, link is automatically considered validated
        data["is_validated_by_admin"] = True if user.is_validated_by_admin and auth_user.is_staff_for_association(association.id) else False

        return super().validate(data)

    def create(self, validated_data):
        auth_user = self.context["request"].user
        instance = super().create(validated_data)

        # Sending mail to dedicated managers : asking for AssociationUser link validation
        if validated_data.get("user").is_validated_by_admin and not auth_user.is_staff_for_association(validated_data.get("association").id):
            current_site = get_current_site(self.context["request"])
            context = {
                "site_domain": f"https://{current_site.domain}",
                "site_name": current_site.name,
                "user_association_url": f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_USER_ASSOCIATION_VALIDATE_PATH}",
            }
            template = MailTemplate.objects.get(code="MANAGER_ACCOUNT_ASSOCIATION_USER_CREATION")
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=list(
                    Institution.objects.get(id=validated_data["association"].institution_id)
                    .default_institution_managers()
                    .values_list("email", flat=True)
                ),
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(self.context["request"].user, self.context["request"], context),
            )
        return instance


class AssociationUserUpdateSerializer(serializers.ModelSerializer):
    """Serializer for user-associations change."""

    class Meta:
        model = AssociationUser
        fields = [
            "is_president",
            "can_be_president_from",
            "can_be_president_to",
            "is_validated_by_admin",
            "is_vice_president",
            "is_secretary",
            "is_treasurer",
        ]
