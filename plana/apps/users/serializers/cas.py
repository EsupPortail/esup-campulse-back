"""Special serializers used to interact with CAS."""
from __future__ import annotations

import typing

from allauth.socialaccount.models import EmailAddress, SocialLogin
from allauth_cas.views import AuthAction
from cas import CASClient, CASClientBase
from dj_rest_auth.serializers import LoginSerializer
from django.conf import settings
from django.db import IntegrityError
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers

from plana.apps.users.adapter import CASAdapter
from plana.apps.users.models.user import User
from plana.apps.users.provider import CASProvider

if typing.TYPE_CHECKING:  # pragma: no cover
    from plana.apps.users.views import CASLogin


class CASSerializer(LoginSerializer):
    """Main serializer."""

    ticket = serializers.CharField(required=True)
    service = serializers.URLField(required=True)
    password = serializers.CharField(required=False)

    def validate(self, attrs):
        """
        CAS Validation.

        Get the username from the CAS Server from the ticket and service url.
        Log in the user.
        Add it to the serializer attributes.
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
            try:
                login.save(request, connect=True)
                EmailAddress.objects.create(
                    email=login.account.user.email,
                    verified=True,
                    primary=True,
                    user_id=login.account.user.id,
                )
                attrs["user"] = login.account.user
                user = User.objects.get(email=attrs["user"].email)
                user.is_student = (
                    True if extra.get("affiliation", "") == "employee" else False
                )
                user.save()
            except IntegrityError:
                pass
        else:
            attrs["user"] = login.account.user
            user = User.objects.get(email=attrs["user"].email)
            if user.get_user_groups().count() == 0:
                raise exceptions.ValidationError(
                    _("Account registration must be completed.")
                )

        return attrs

    def validate_service(self, value):
        """Check if the service is authorized in the configuration file."""
        if value not in settings.CAS_AUTHORIZED_SERVICES:
            raise exceptions.ValidationError(_(f"{value} is not a valid service"))
        return value

    def get_client(
        self,
        request: HttpRequest,
        adapter: CASAdapter,
        service_url: str,
        action: str = AuthAction.AUTHENTICATE,
    ) -> CASClientBase:
        """Get CAS informations."""
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
        """Get CAS adapter informations."""
        adapter_class = getattr(view, "adapter_class", None)
        if not adapter_class:
            raise serializers.ValidationError(
                _("Can not find adapter_class attribute on view")
            )
        adapter = adapter_class(request)
        return adapter
