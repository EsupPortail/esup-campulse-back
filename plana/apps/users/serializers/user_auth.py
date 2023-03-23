"""dj-rest-auth overrided serializers."""
import datetime

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
from rest_framework import exceptions

from plana.apps.users.models.user import User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class PasswordChangeSerializer(DJRestAuthPasswordChangeSerializer):
    """Overrided PasswordChangeSerializer to prevent CAS users to change their passwords."""

    def save(self):
        request = self.context.get("request")
        try:
            user = User.objects.get(email=request.user.email)
            if user.is_cas_user():
                raise exceptions.ValidationError(
                    {"detail": [_("Unable to change the password of a CAS account.")]}
                )
            self.set_password_form.save()
            user.password_last_change_date = datetime.datetime.today()
            user.save(update_fields=["password_last_change_date"])
            if not self.logout_on_password_change:
                from django.contrib.auth import update_session_auth_hash

                update_session_auth_hash(self.request, self.user)
        except ObjectDoesNotExist:
            pass


class PasswordResetSerializer(DJRestAuthPasswordResetSerializer):
    """Overrided PasswordResetSerializer to prevent CAS users to reset their passwords."""

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
            pass


class PasswordResetConfirmSerializer(DJRestAuthPasswordResetConfirmSerializer):
    """Overrided PasswordResetConfirmSerializer to send a email when password is reset."""

    def save(self):
        self.user.password_last_change_date = datetime.datetime.today()
        self.user.save(update_fields=["password_last_change_date"])
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
