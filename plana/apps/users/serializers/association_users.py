"""
Serializers describing fields used on links between users and associations.
"""
from rest_framework import serializers

from plana.apps.associations.serializers.association import (
    AssociationMandatoryDataSerializer,
)
from plana.apps.users.models.association_users import AssociationUsers
from plana.apps.users.models.user import User


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
            "has_office_status",
            "is_president",
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
            "has_office_status",
            "is_president",
            "association",
        ]
