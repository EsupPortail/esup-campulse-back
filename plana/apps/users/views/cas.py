"""Special views dedicated to CAS login and operations."""

import json

from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LogoutView
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.db import transaction
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, generics, permissions

from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from allauth.socialaccount.providers.openid_connect.provider import OpenIDConnectProvider

from plana.apps.history.models import History
from plana.apps.users.models import User
from plana.apps.users.serializers.user import CustomCASDataRegisterSerializer
from plana.libs.mail_template.models import MailTemplate
from plana.utils import send_mail


class CASOpenIDConnectAdapter(OpenIDConnectProvider.oauth2_adapter_class):
    def __init__(self, request):
        super().__init__(request, provider_id="cas")


class PKCEOAuth2Client(OAuth2Client):
    """OAuth2 client that forwards the PKCE ``code_verifier`` to the token endpoint.

    dj-rest-auth's ``SocialLoginSerializer`` only passes the authorization
    ``code`` to ``get_access_token()`` and silently drops the ``code_verifier``
    sent by the frontend. When CAS is configured with PKCE, the token exchange
    fails (``invalid_grant``) because the verifier is missing. This client
    recovers the verifier from the request body and forwards it to CAS.
    """

    def get_access_token(self, code, pkce_code_verifier=None, extra_data=None):
        if pkce_code_verifier is None:
            pkce_code_verifier = self._extract_code_verifier()
        return super().get_access_token(
            code, pkce_code_verifier=pkce_code_verifier, extra_data=extra_data
        )

    def _extract_code_verifier(self):
        """Read ``code_verifier`` from the JSON request body (sent by the frontend)."""
        try:
            payload = json.loads(self.request.body) if self.request.body else {}
        except (ValueError, TypeError):
            return None
        if isinstance(payload, dict):
            return payload.get("code_verifier")
        return None


class OIDCLogin(SocialLoginView):
    """
    /users/auth/cas/login/ route.

    POST : Authenticates a user through CAS with django-allauth-cas and dj-rest-auth.
    """

    adapter_class = CASOpenIDConnectAdapter
    callback_url = "http://localhost:8000/"
    client_class = PKCEOAuth2Client
    # client_class = OAuth2Client


class OIDCLogout(LogoutView):
    """
    /users/auth/cas/logout/ route.

    GET : Logs out a user authenticated with CAS out.

    POST : Logs out a user authenticated with CAS out.
    """
    pass


class CASDataRegisterView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = CustomCASDataRegisterSerializer
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ["patch"]

    def get_object(self):
        user = self.request.user
        if user.is_validated_by_admin or not user.is_cas_user:
            raise exceptions.PermissionDenied(
                detail=_("Cannot update registration data for an already validated account or a local account.")
            )
        return user

    @transaction.atomic
    def perform_update(self, serializer):
        serializer.save()

        # Send manager notification email when data submitted
        current_site = get_current_site(self.request)
        context = {"site_domain": current_site.domain, "site_name": current_site.name, "account_url": (
            f"{settings.EMAIL_TEMPLATE_FRONTEND_URL}{settings.EMAIL_TEMPLATE_ACCOUNT_VALIDATE_PATH}{self.request.user.pk}"
        )}
        History.objects.create(action_title="USER_REGISTERED", action_user_id=self.request.user.pk)
        template = MailTemplate.objects.get(code="MANAGER_ACCOUNT_LDAP_CREATION")
        send_mail(
            from_=settings.DEFAULT_FROM_EMAIL,
            to_=self.request.user.get_user_default_manager_emails(),
            subject=template.subject.replace("{{ site_name }}", context["site_name"]),
            message=template.parse_vars(self.request.user, self.request, context),
        )
