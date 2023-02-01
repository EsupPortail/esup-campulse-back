"""
Serializers describing fields used on links between users and associations.
"""
from rest_framework import serializers

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
        fields = [
            "id",
            "user",
            "role_name",
            "is_president",
            "can_be_president",
            "association",
        ]


class AssociationUsersCreationSerializer(serializers.ModelSerializer):
    """
    Serializer to create the link (without all association details).
    """

    user = serializers.SlugRelatedField(
        slug_field="username", queryset=User.objects.all()
    )

    class Meta:
        model = AssociationUsers
        fields = [
            "user",
            "role_name",
            "is_president",
            "can_be_president",
            "association",
        ]


class AssociationUsersUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer used to patch AssociationUsers fields.
    """

    class Meta:
        model = AssociationUsers
        fields = [
            "role_name",
            "is_president",
            "can_be_president",
        ]
