from __future__ import annotations

import typing

from allauth.socialaccount.models import SocialLogin
from allauth_cas.views import AuthAction
from cas import CASClient, CASClientBase
from dj_rest_auth.serializers import LoginSerializer
from django.conf import settings
from django.http import HttpRequest
from django.utils.translation import ugettext_lazy as _
from rest_framework import exceptions, serializers

from plana.apps.users.adapter import CASAdapter
from plana.apps.users.provider import CASProvider

if typing.TYPE_CHECKING:
    from plana.apps.users.views import CASLogin


class CASSerializer(LoginSerializer):

    ticket = serializers.CharField(required=True)
    service = serializers.URLField(required=True)
    password = serializers.CharField(required=False)

    def validate(self, attrs):
        """
        We get the username from the CAS Server from the ticket and service url, log in the user
        and add it to the serializer attributes
        """
        view = self.context.get("view")
        request = self.context.get("request")

        if not view:
            raise exceptions.ValidationError(
                _("View is not defined, pass it as a context variable")
            )

        adapter = self.get_adapter(request, view)

        client = self.get_client(request, adapter, attrs["service"])

        # Check ticket
        # Response format :
        # - success : username, attributes, pgtiou
        # - error: None, {}, None
        response = client.verify_ticket(attrs.get("ticket"))
        uid, extra, _pgtiou = response

        if not uid:
            raise exceptions.ValidationError(
                _("CAS server doesn't validate the ticket")
            )

        data = (uid, extra or {})

        login: SocialLogin = adapter.complete_login(request, data)
        login.lookup()
        if not login.is_existing:
            login.save(request, connect=True)
        attrs["user"] = login.account.user

        return attrs

    def validate_service(self, value):
        if value not in settings.CAS_AUTHORIZED_SERVICES:
            raise exceptions.ValidationError(
                _("%(service)s is not a valid service" % {"service": value})
            )
        return value

    def get_client(
        self,
        request: HttpRequest,
        adapter: CASAdapter,
        service_url: str,
        action: str = AuthAction.AUTHENTICATE,
    ) -> CASClientBase:
        provider: CASProvider = adapter.get_provider(request)
        auth_params = provider.get_auth_params(request, action)
        service_url = service_url or adapter.get_service_url(request)
        client = CASClient(
            service_url=service_url,
            server_url=adapter.url,
            version=adapter.version,
            renew=adapter.renew,
            extra_login_params=auth_params,
        )

        return client

    def get_adapter(self, request: HttpRequest, view: CASLogin) -> CASAdapter:
        adapter_class = getattr(view, "adapter_class", None)
        if not adapter_class:
            raise serializers.ValidationError(
                _("Can not find adapter_class attribute on view")
            )
        adapter = adapter_class(request)
        return adapter
