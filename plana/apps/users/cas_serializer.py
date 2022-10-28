import cas
from allauth.socialaccount.models import SocialLogin
from allauth_cas.exceptions import CASAuthenticationError
from allauth_cas.views import AuthAction
from rest_framework import serializers
from django.utils.translation import ugettext_lazy as _



class CASSerializer(serializers.Serializer):

    ticket = serializers.CharField(required=True)

    def validate(self, attrs):
        """
        We need
        """
        view = self.context.get("view")
        request = self.context.get("request")

        if not view:
            raise serializers.ValidationError(
                _("View is not defined, pass it as a context variable")
            )

        adapter = self.get_adapter(request, view)

        client = self.get_client(request, adapter)

        # Check ticket
        # Response format :
        # - success : username, attributes, pgtiou
        # - error: None, {}, None
        response = client.verify_ticket(attrs.get("ticket"))
        uid, extra, _ = response

        if not uid:
            raise CASAuthenticationError(
                _("CAS server doesn't validate the ticket")
            )

        data = (uid, extra or {})

        login: SocialLogin = adapter.complete_login(request, data)
        if not login.is_existing:
            login.lookup()
            login.save(request, connect=True)
        attrs["user"] = login.account.user

        return attrs

    def get_client(self, request, adapter, action=AuthAction.AUTHENTICATE):
        provider = adapter.get_provider(request)
        auth_params = provider.get_auth_params(request, action)
        service_url = adapter.get_service_url(request)
        client = cas.CASClient(
            service_url=service_url,
            server_url=adapter.url,
            version=adapter.version,
            renew=adapter.renew,
            extra_login_params=auth_params,
        )

        return client

    def get_adapter(self, request, view):
        adapter_class = getattr(view, "adapter_class", None)
        if not adapter_class:
            raise serializers.ValidationError(
                _("Can not find adapter_class attribute on view")
            )
        adapter = adapter_class(request)
        return adapter
