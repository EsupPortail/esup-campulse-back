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
    def send_mail(self, template_prefix, email, context):
        """
        Overrided send_mail method to use the one from the utils file.
        """
        # msg = self.render_mail(template_prefix, email, context)
        # msg.send()
        if template_prefix == "account/email/password_reset_key":
            template = MailTemplate.objects.get(code="PASSWORD_RESET_KEY")
            user = User.objects.get(email=email)
            request = context.get("request")
            current_site = get_current_site(request)
            uid = re.match(r"^(.*)/(.*)/(.*)/$", context["password_reset_url"]).group(2)
            token = re.match(r"^(.*)/(.*)/(.*)/$", context["password_reset_url"]).group(
                3
            )
            context["site_domain"] = current_site
            context["site_name"] = current_site
            context["username"] = user.username
            context["password_reset_url"] = (
                settings.EMAIL_TEMPLATE_PASSWORD_RESET_URL
                + "?uid="
                + uid
                + "&token="
                + token
            )
            send_mail(
                from_=settings.DEFAULT_FROM_EMAIL,
                to_=email,
                subject=template.subject,
                message=template.parse_vars(user, request, context),
            )

    def send_confirmation_mail(self, request, emailconfirmation, signup):
        """
        Overrided send_confirmation_email method to get custom template.
        """
        template = MailTemplate.objects.get(code="EMAIL_CONFIRMATION_MESSAGE")
        user = User.objects.get(email=emailconfirmation.email_address)
        current_site = get_current_site(request)
        activate_url = (
            settings.EMAIL_TEMPLATE_ACCOUNT_CONFIRMATION_URL
            + "?key="
            + emailconfirmation.key
        )
        ctx = {
            "site_domain": current_site,
            "site_name": current_site,
            "activate_url": activate_url,
        }
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=emailconfirmation.email_address,
            subject=template.subject,
            message=template.parse_vars(user, request, ctx),
        )


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    pass


class CASAdapter(AllAuthCASAdapter):
    """
    Subclass CASAdapter to give the configuration as a CAS client.
    """

    provider_id = CASProvider.id
    url = settings.CAS_SERVER
    version = settings.CAS_VERSION

    def get_provider(self, request):
        return self.provider
