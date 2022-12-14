"""
Serializers describing fields used on users and related forms.
"""
from allauth.account.adapter import get_adapter
from dj_rest_auth.serializers import (
    PasswordChangeSerializer as DJRestAuthPasswordChangeSerializer,
)
from dj_rest_auth.serializers import (
    PasswordResetSerializer as DJRestAuthPasswordResetSerializer,
)
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers

from plana.apps.users.models.user import User


class UserSerializer(serializers.ModelSerializer):
    """
    Main serializer.
    """

    is_cas = serializers.SerializerMethodField("is_cas_user")

    def is_cas_user(self, user) -> bool:
        """
        Content from calculated field "is_cas" (True if user registred through CAS, or False).
        """
        return user.is_cas_user()

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
            "is_validated_by_admin",
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
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = request.data
        adapter.save_user(request, user, self)

        user.username = self.cleaned_data["email"]
        try:
            user.phone = self.cleaned_data["phone"]
        except KeyError:
            ...

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
