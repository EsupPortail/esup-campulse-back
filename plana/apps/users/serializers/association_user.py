"""Serializers describing fields used on links between users and associations."""

from rest_framework import serializers

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import AssociationMandatoryDataSerializer
from plana.apps.users.models.user import AssociationUser, User
from plana.apps.users.serializers.user import UserNameSerializer



class AssociationUserSerializer(serializers.ModelSerializer):
    """Main serializer."""

    user = UserNameSerializer(read_only=True)
    association = AssociationMandatoryDataSerializer(read_only=True)

    class Meta:
        model = AssociationUser
        fields = "__all__"


class AssociationUserCreateSerializer(serializers.ModelSerializer):
    """Serializer for user-associations creation."""

    user = serializers.SlugRelatedField(slug_field="username", queryset=User.objects.all())
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
