"""
Links the CAS provider to the CAS views.
"""
import re

from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth_cas.views import CASAdapter as AllAuthCASAdapter
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site

from plana.apps.users.models.user import User
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail

from .provider import CASProvider


class PlanAAdapter(DefaultAccountAdapter):
    """
    Default adapter for local accounts.
    """

    def send_mail(self, template_prefix, email, context):
        """
        Overrided send_mail django-allauth method to use the one from the utils file.
        """
        user = User.objects.get(email=email)
        manager = User.objects.filter(groups__name="Gestionnaire SVU").first()
        request = context.get("request")
        current_site = get_current_site(request)
        template = MailTemplate.objects.all()
        context["site_domain"] = current_site.domain
        context["site_name"] = current_site.name
        context["username"] = user.username
        context["first_name"] = user.first_name
        context["last_name"] = user.last_name
        context["manager_email_address"] = manager.email

        if template_prefix == "account/email/email_confirmation_signup":
            template = MailTemplate.objects.get(code="EMAIL_CONFIRMATION_MESSAGE")
            key = context['key']
            context[
                "activate_url"
            ] = f"{settings.EMAIL_TEMPLATE_ACCOUNT_CONFIRMATION_URL}?key={key}"

        elif template_prefix == "account/email/password_reset_key":
            template = MailTemplate.objects.get(code="PASSWORD_RESET_KEY")
            password_reset_url_parts = re.match(
                r"^(.*)/(.*)/(.*)/$", context["password_reset_url"]
            )
            uid = password_reset_url_parts.group(2)
            token = password_reset_url_parts.group(3)
            context[
                "password_reset_url"
            ] = f"{settings.EMAIL_TEMPLATE_PASSWORD_RESET_URL}?uid={uid}&token={token}"

        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=email,
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(user, request, context),
        )


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Default adapter for CAS accounts.
    """

    pass


class CASAdapter(AllAuthCASAdapter):
    """
    Subclass CASAdapter to give the configuration as a CAS client.
    """

    provider_id = CASProvider.id
    url = settings.CAS_SERVER
    version = settings.CAS_VERSION

    def get_provider(self, request):
        """
        Get the provider.
        """
        return self.provider
