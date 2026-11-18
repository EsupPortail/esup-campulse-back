"""Links the CAS provider to the CAS views."""
import re

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from plana.apps.users.models.user import User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class PlanAAdapter(DefaultAccountAdapter):
    """Default adapter for local accounts."""

    def send_mail(self, template_prefix, email, context):
        """Override send_mail django-allauth method to use the one from the utils file."""
        user = User.objects.get(email=email)
        request = context.get("request")
        current_site = get_current_site(request)
        template = MailTemplate.objects.all()
        context["site_domain"] = current_site.domain
        context["site_name"] = current_site.name
        context["username"] = user.username
        context["first_name"] = user.first_name
        context["last_name"] = user.last_name
        context["manager_email_address"] = ','.join(user.get_user_default_manager_emails())

        if template_prefix in [
            "account/email/email_confirmation_signup",
            "account/email/email_confirmation",
        ]:
            if template_prefix == "account/email/email_confirmation_signup":
                template = MailTemplate.objects.get(code="USER_ACCOUNT_CREATION")
            elif template_prefix == "account/email/email_confirmation":
                template = MailTemplate.objects.get(code="USER_ACCOUNT_EMAIL_RECONFIRMATION")
            key = context["key"]
            context["activate_url"] = (
                f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_ACCOUNT_CONFIRMATION_PATH}?key={key}"
            )

        elif template_prefix == "account/email/password_reset_key":
            template = MailTemplate.objects.get(code="USER_ACCOUNT_PASSWORD_RESET")
            password_reset_url_parts = re.match(r"^(.*)/(.*)/(.*)/$", context["password_reset_url"])
            uid = password_reset_url_parts.group(2)
            token = password_reset_url_parts.group(3)
            context["password_reset_url"] = (
                f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_PASSWORD_RESET_PATH}?uid={uid}&token={token}"
            )

        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=email,
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(user, request, context),
        )


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """Minimal Adapter to plug dj-rest-auth on 'cas' OIDC provider"""

    def populate_user(self, request, sociallogin, data):
        """Fills the user attributes from the provider's JWT claims"""
        print(data)
        user = super().populate_user(request, sociallogin, data)

        # Get claims stored in extra_data by the provider
        extra_data = sociallogin.account.extra_data.get("userinfo", {})
        print(extra_data)
        user.username = extra_data.get(settings.CAS_ATTRIBUTES_NAMES["uid"], user.username)
        user.email = extra_data.get(settings.CAS_ATTRIBUTES_NAMES["email"], user.email)
        user.first_name = extra_data.get(settings.CAS_ATTRIBUTES_NAMES["first_name"], user.first_name)
        user.last_name = extra_data.get(settings.CAS_ATTRIBUTES_NAMES["last_name"], user.last_name)

        affiliation = extra_data.get(settings.CAS_ATTRIBUTES_NAMES["is_student"], "")
        user.is_student = settings.CAS_ATTRIBUTES_VALUES["is_student"] == affiliation

        return user
