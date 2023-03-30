"""Serializers describing fields used on associations."""
from rest_framework import serializers

from plana.apps.associations.models.activity_field import ActivityField
from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.fields import ThumbnailField
from plana.apps.institutions.models.institution import Institution
from plana.apps.institutions.models.institution_component import InstitutionComponent
from plana.apps.users.models.user import AssociationUser


class AssociationAllDataReadSerializer(serializers.ModelSerializer):
    """Main serializer."""

    institution = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all())
    institution_component = serializers.PrimaryKeyRelatedField(
        queryset=InstitutionComponent.objects.all()
    )
    activity_field = serializers.PrimaryKeyRelatedField(
        queryset=ActivityField.objects.all()
    )
    path_logo = ThumbnailField(sizes=["detail"])

    class Meta:
        model = Association
        fields = "__all__"


class AssociationAllDataUpdateSerializer(serializers.ModelSerializer):
    """Main serializer."""

    institution = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all())
    institution_component = serializers.PrimaryKeyRelatedField(
        queryset=InstitutionComponent.objects.all()
    )
    activity_field = serializers.PrimaryKeyRelatedField(
        queryset=ActivityField.objects.all()
    )

    class Meta:
        model = Association
        fields = "__all__"


class AssociationPartialDataSerializer(serializers.ModelSerializer):
    """Smaller serializer to return only some of the informations of an association."""

    institution = serializers.PrimaryKeyRelatedField(queryset=Institution.objects.all())
    institution_component = serializers.PrimaryKeyRelatedField(
        queryset=InstitutionComponent.objects.all()
    )
    activity_field = serializers.PrimaryKeyRelatedField(
        queryset=ActivityField.objects.all()
    )
    path_logo = ThumbnailField(sizes=["list"])

    class Meta:
        model = Association
        fields = [
            "id",
            "institution",
            "institution_component",
            "activity_field",
            "name",
            "acronym",
            "email",
            "is_enabled",
            "is_public",
            "is_site",
            "alt_logo",
            "path_logo",
        ]


class AssociationMandatoryDataSerializer(serializers.ModelSerializer):
    """Smaller serializer to return only the main informations of an association."""

    class Meta:
        model = Association
        fields = [
            "id",
            "name",
            "is_enabled",
            "is_public",
            "is_site",
            "institution",
        ]


class AssociationNameSerializer(serializers.ModelSerializer):
    """Smaller serializer used in a simple name list of all associations."""

    has_president = serializers.SerializerMethodField("is_president_in_association")

    def is_president_in_association(self, association) -> bool:
        """Check if a president has been linked to an association."""
        return AssociationUser.objects.filter(
            association_id=association.id, is_president=True
        ).exists()

    class Meta:
        model = Association
        fields = [
            "id",
            "name",
            "has_president",
            "institution",
        ]
