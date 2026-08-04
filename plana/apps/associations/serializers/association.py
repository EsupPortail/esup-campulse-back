"""Serializers describing fields used on associations."""
import json
import re

from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.translation import gettext_lazy as _
from rest_framework import serializers

from plana.apps.associations.models.association import Association
from plana.apps.associations.serializers.activity_field import ActivityFieldSerializer
from plana.apps.associations.serializers.fields import ThumbnailField
from plana.apps.history.models import History
from plana.apps.institutions.serializers.institution import InstitutionSerializer
from plana.apps.institutions.serializers.institution_component import (
    InstitutionComponentSerializer,
)
from plana.libs.mail_template.models import MailTemplate
from plana.utils import PHONE_REGEX_PATTERN, normalize_object_name, send_mail

RESTRICTED_FIELDS = [
    "amount_members_allowed",
    "can_submit_projects",
    "creation_date",
    "institution",
    "is_enabled",
    "is_public",
    "is_site",
]


class AssociationAllDataReadSerializer(serializers.ModelSerializer):
    """Main serializer."""

    institution = InstitutionSerializer(read_only=True)
    institution_component = InstitutionComponentSerializer(read_only=True)
    activity_field = ActivityFieldSerializer(read_only=True)
    path_logo = ThumbnailField(sizes=["detail"])
    calculated_expiration_date = serializers.ReadOnlyField()

    def to_representation(self, obj):
        """Don't send confidential values depending on the user doing the request."""
        request = self.context.get('request', None)
        representation = super().to_representation(obj)

        if request.user.is_anonymous or (
            not request.user.is_anonymous
            and not request.user.is_in_association(obj.id)
            and not request.user.has_perm("associations.view_association_all_fields")
        ):
            private_fields = ["phone", "president_phone", "can_submit_projects"]
            for private_field in private_fields:
                representation.pop(private_field)

        return representation

    class Meta:
        model = Association
        fields = "__all__"


class AssociationAllDataUpdateSerializer(serializers.ModelSerializer):
    """Main serializer."""
    path_logo = serializers.ImageField(required=False, allow_null=True)

    def __init__(self, *args, **kwargs):
        """Custom init to force readonly on restricted fields if user doesn't have the correct permission"""
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        # Part of a more complex process, only Association field never editable here
        self.fields["charter_status"].read_only = True

        if request and hasattr(request, "user"):
            if not request.user.has_perm("associations.change_association_all_fields"):
                for field_name in RESTRICTED_FIELDS:
                    if field_name in self.fields:
                        self.fields[field_name].read_only = True

    def validate_phone(self, value):
        """Check phone field with a regex."""
        if value == '':
            return value
        if not re.match(PHONE_REGEX_PATTERN, value):
            raise serializers.ValidationError("Wrong phone number format.")
        return value

    def validate_path_logo(self, value):
        """Force image mime types for association logos"""
        if value:
            content_type = getattr(value, "content_type", None)
            if content_type not in settings.ALLOWED_IMAGE_MIME_TYPES:
                raise serializers.ValidationError(_("Wrong media type for images."))
        return value

    def validate_social_networks(self, value):
        """Validate correct JSON format and keys for social_networks JSONField (allows empty list too)"""
        allowed_keys = {"type", "location"}

        if isinstance(value, str):
            value = json.loads(value)

        if not isinstance(value, list):
            raise serializers.ValidationError({"list_expected": _("Social networks field expected a list of items.")})

        for item in value:
            if not isinstance(item, dict) or set(item.keys()) != allowed_keys:
                raise serializers.ValidationError({"wrong_params": _("Wrong social networks parameters : keys 'type' and 'location' are mandatory.")})
            if not all(isinstance(v, str) for v in item.values()):
                raise serializers.ValidationError({"wrong_value_types": _("Wrong social_networks values : only strings are authorized.")})

        return value

    def validate_amount_members_allowed(self, value):
        """Cannot set a lower members amount than the association already has"""
        if self.instance:
            current_count = self.instance.associationuser_set.count()
            if value < current_count:
                raise serializers.ValidationError(_("Cannot set lower amount of members in this association."))
        return value

    def validate(self, data):
        """Custom validation for some fields depending on others"""
        if (data.get("is_public") and not self.instance.is_enabled) or data.get("is_enabled") is False:
            data["is_public"] = False

        if data.get("institution_component") or data.get("institution"):
            institution_component = data.get("institution_component", self.instance.institution_component if self.instance else None)
            institution = data.get("institution", self.instance.institution if self.instance else None)
            if institution_component and institution and institution_component.institution_id != institution.id:
                raise serializers.ValidationError({
                    "inconsistent_institution": _("Institution component must be related to the same institution as the association.")
                })
        return data

    def update(self, instance, validated_data):
        request = self.context.get("request")
        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
            "manager_email_address": request.user.email,
        }

        if "can_submit_projects" in validated_data and validated_data["can_submit_projects"] != instance.can_submit_projects:
            new_state = validated_data["can_submit_projects"]
            template_code = "USER_OR_ASSOCIATION_PROJECT_SUBMISSION_ENABLED" if new_state else "USER_OR_ASSOCIATION_PROJECT_SUBMISSION_DISABLED"
            template = MailTemplate.objects.get(code=template_code)
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=instance.email,
                subject=template.subject.replace("{{ site_name }}", context["site_name"]),
                message=template.parse_vars(request.user, request, context),
            )

        context["first_name"] = request.user.first_name
        context["last_name"] = request.user.last_name
        context["association_name"] = instance.name
        History.objects.create(
            action_title="ASSOCIATION_CHANGED", action_user_id=request.user.pk, association_id=instance.id
        )
        template = MailTemplate.objects.get(code="USER_ACCOUNT_ASSOCIATION_CHANGE_CONFIRMATION")
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=request.user.email,
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(request.user, request, context),
        )

        return super().update(instance, validated_data)

    class Meta:
        model = Association
        fields = "__all__"


class AssociationPartialDataSerializer(serializers.ModelSerializer):
    """Smaller serializer to return only some of the informations of an association."""

    institution = InstitutionSerializer(read_only=True)
    institution_component = InstitutionComponentSerializer(read_only=True)
    activity_field = ActivityFieldSerializer(read_only=True)
    path_logo = serializers.SerializerMethodField("cached_logo_url")

    def cached_logo_url(self, association) -> dict[str, str]:
        """Return cached logo URL instead of calculated one which is slower."""
        if association.path_logo.name != '':
            logo_name = f"{association.path_logo.name.split('.')[0]}_list.{association.path_logo.name.split('.')[1]}"
            return {
                "list": f"{settings.AWS_S3_ENDPOINT_URL}/{settings.AWS_STORAGE_PUBLIC_BUCKET_NAME}/thumbnails/{logo_name}"
            }
        return None

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
            "path_logo",
            "charter_status",
            "charter_date",
        ]


class AssociationMandatoryDataSerializer(serializers.ModelSerializer):
    """Smaller serializer to return only the main informations of an association."""

    class Meta:
        model = Association
        fields = [
            "id",
            "name",
            "acronym",
            "email",
            "is_enabled",
            "is_public",
            "is_site",
            "institution",
            "can_submit_projects"
        ]

    def validate(self, data):
        user = self.context['request'].user

        if "institution" not in data:
            institutions = user.get_user_managed_institutions()
            if institutions.count() == 1:
                data["institution"] = institutions.first()
            else:
                raise serializers.ValidationError({"no_institution": _("No institution given.")})

        if not user.has_perm("associations.add_association_any_institution") and not user.is_staff_in_institution(data["institution"]):
            raise serializers.ValidationError({"wrong_institution": _("Not allowed to create an association for this institution.")})

        restricted_fields = ["is_site", "is_public"]
        if any(bool(data.get(field)) for field in restricted_fields) and not user.has_perm("associations.add_association_all_fields"):
            raise serializers.ValidationError({"restricted_fields": _("Not allowed to create an association with restricted fields.")})

        # Removes spaces, uppercase and accented characters to avoid similar association names.
        associations = Association.objects.all()
        for association in associations:
            if normalize_object_name(data["name"]) == normalize_object_name(association.name):
                raise serializers.ValidationError({"similar_name": _("Association name already taken.")})

        if "is_site" not in data:
            data["is_site"] = settings.ASSOCIATION_IS_SITE_DEFAULT
        data["is_enabled"] = True  # Always enabled at creation

        return data


class AssociationNameSerializer(serializers.ModelSerializer):
    """Smaller serializer used in a simple name list of all associations."""

    has_president = serializers.BooleanField()

    class Meta:
        model = Association
        fields = [
            "id",
            "name",
            "has_president",
            "institution",
        ]


class AssociationStatusSerializer(serializers.ModelSerializer):
    """Serializer for status field."""

    class Meta:
        model = Association
        fields = ["charter_status"]
