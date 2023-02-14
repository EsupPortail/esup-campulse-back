"""
Serializers describing fields used on links between users and associations.
"""
from rest_framework import serializers

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.association import (
    AssociationMandatoryDataSerializer,
)
from plana.apps.users.models.user import AssociationUsers, User


class AssociationUsersSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )
    association = AssociationMandatoryDataSerializer()

    class Meta:
        model = AssociationUsers
        fields = "__all__"


class AssociationUsersCreateSerializer(serializers.ModelSerializer):
    """
    Serializer for user-associations creation.
    """

    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = AssociationUsers
        fields = [
            "user",
            "is_president",
            "can_be_president",
            "is_validated_by_admin",
            "is_secretary",
            "is_treasurer",
            "association",
        ]


class AssociationUsersUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for user-associations change.
    """

    class Meta:
        model = AssociationUsers
        fields = [
            "is_president",
            "can_be_president",
            "is_validated_by_admin",
            "is_secretary",
            "is_treasurer",
        ]


class AssociationUsersDeleteSerializer(serializers.ModelSerializer):
    """
    Serializer for user-associations deletion.
    """

    user = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    association = serializers.PrimaryKeyRelatedField(queryset=Association.objects.all())

    class Meta:
        model = AssociationUsers
        fields = [
            "user",
            "association",
        ]
