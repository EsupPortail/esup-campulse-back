"""
Serializers describing fields used on users and related forms.
"""
from allauth.account.adapter import get_adapter
from dj_rest_auth.serializers import (
    PasswordChangeSerializer as DJRestAuthPasswordChangeSerializer,
)
from dj_rest_auth.serializers import (
    PasswordResetConfirmSerializer as DJRestAuthPasswordResetConfirmSerializer,
)
from dj_rest_auth.serializers import (
    PasswordResetSerializer as DJRestAuthPasswordResetSerializer,
)
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import extend_schema_field
from rest_framework import exceptions, serializers

from plana.apps.associations.serializers.association import (
    AssociationMandatoryDataSerializer,
)
from plana.apps.users.models.user import GroupInstitutionUsers, User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class UserSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    phone = serializers.CharField(required=False, allow_blank=True)
    is_cas = serializers.SerializerMethodField("is_cas_user")
    has_validated_email = serializers.SerializerMethodField("has_validated_email_user")
    associations = AssociationMandatoryDataSerializer(many=True, read_only=True)
    groups = serializers.SerializerMethodField()

    @extend_schema_field(OpenApiTypes.OBJECT)
    def get_groups(self, user):
        """
        Return groups-institutions-users links.
        """
        return GroupInstitutionUsers.objects.filter(user_id=user.pk).values()

    def is_cas_user(self, user) -> bool:
        """
        Content from calculated field "is_cas" (True if user registered through CAS, or False).
        """
        return user.is_cas_user()

    def has_validated_email_user(self, user) -> bool:
        """
        Content from calculated field "has_validated_email"
            (True if user finished the registration, or False).
        """
        return user.has_validated_email_user()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "phone",
            "is_cas",
            "has_validated_email",
            "is_validated_by_admin",
            "associations",
            "groups",
        ]


class CustomRegisterSerializer(serializers.ModelSerializer):
    """
    Used for the user registration form (to parse the phone field).
    """

    phone = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "phone")

    """
    def get_validation_exclusions(self):
        exclusions = super(CustomRegisterSerializer, self).get_validation_exclusions()
        return exclusions + ["phone"]
    """

    """
    def validate_email(self, value):
        ModelClass = self.Meta.model
        if ModelClass.objects.filter(email=value).exists():
            raise serializers.ValidationError(
                _("This email address is already in use.")
            )
        return value
    """

    def save(self, request):
        self.cleaned_data = request.data
        if self.cleaned_data["email"].split('@')[1] in settings.RESTRICTED_DOMAINS:
            raise exceptions.ValidationError(
                {"detail": [_("Unistra users cannot create local accounts.")]}
            )
        adapter = get_adapter()
        user = adapter.new_user(request)
        adapter.save_user(request, user, self)

        user.username = self.cleaned_data["email"]
        if "phone" in self.cleaned_data:
            user.phone = self.cleaned_data["phone"]

        user.save()
        return user


class PasswordChangeSerializer(DJRestAuthPasswordChangeSerializer):
    """
    Overrided PasswordChangeSerializer to prevent CAS users to change their passwords.
    """

    def save(self):
        request = self.context.get("request")
        try:
            user = User.objects.get(email=request.user.email)
            if user.is_cas_user():
                raise exceptions.ValidationError(
                    {"detail": [_("Unable to change the password of a CAS account.")]}
                )
            self.set_password_form.save()
            if not self.logout_on_password_change:
                from django.contrib.auth import update_session_auth_hash

                update_session_auth_hash(self.request, self.user)
        except ObjectDoesNotExist:
            ...


class PasswordResetSerializer(DJRestAuthPasswordResetSerializer):
    """
    Overrided PasswordResetSerializer to prevent CAS users to reset their passwords.
    """

    def save(self):
        if "allauth" in settings.INSTALLED_APPS:
            from allauth.account.forms import default_token_generator
        else:
            from django.contrib.auth.tokens import default_token_generator

        request = self.context.get("request")
        # Set some values to trigger the send_email method.
        opts = {
            "use_https": request.is_secure(),
            "from_email": getattr(settings, "DEFAULT_FROM_EMAIL"),
            "request": request,
            "token_generator": default_token_generator,
        }

        opts.update(self.get_email_options())

        try:
            user = User.objects.get(email=request.data["email"])
            if user.is_cas_user():
                raise exceptions.ValidationError(
                    {"detail": [_("Unable to reset the password of a CAS account.")]}
                )
            self.reset_form.save(**opts)
        except ObjectDoesNotExist:
            ...


class PasswordResetConfirmSerializer(DJRestAuthPasswordResetConfirmSerializer):
    """
    Overrided PasswordResetConfirmSerializer to send a email when password is reset.
    """

    def save(self):
        request = None
        current_site = get_current_site(request)
        context = {
            "site_domain": current_site.domain,
            "site_name": current_site.name,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
        }
        template = MailTemplate.objects.get(code="PASSWORD_RESET_CONFIRMATION")
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=self.user.email,
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(self.user, request, context),
        )
        return self.set_password_form.save()
