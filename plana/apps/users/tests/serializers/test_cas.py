from unittest.mock import patch

from allauth.socialaccount.models import SocialAccount
from allauth_cas import CAS_PROVIDER_SESSION_KEY
from django.contrib.auth.models import Group
from django.test import TestCase, override_settings
from django.utils.translation import ugettext_lazy as _
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory

from plana.apps.users.adapter import CASAdapter
from plana.apps.users.models.user import User
from plana.apps.users.provider import CASProvider
from plana.apps.users.serializers.cas import CASSerializer
from plana.apps.users.views.user import CASLogin


class CASSerializerTest(TestCase):
    def test_get_adapter_returns_adapter_from_view(self):
        request = APIRequestFactory().get("/")
        adapter = CASAdapter
        view = CASLogin.as_view()
        view.adapter_class = adapter

        serializer = CASSerializer()
        returned_adapter = serializer.get_adapter(request, view)

        self.assertIsInstance(
            returned_adapter,
            CASAdapter,
        )

    def test_get_adapter_raises_error_if_adapter_is_not_set_on_view(self):
        request = APIRequestFactory().get("/")
        view = CASLogin.as_view()

        serializer = CASSerializer()
        with self.assertRaises(ValidationError) as ctx:
            serializer.get_adapter(request, view)

        self.assertIn(
            _("Can not find adapter_class attribute on view"),
            ctx.exception.detail,
        )

    def test_get_client_returns_configured_client(self):
        serializer = CASSerializer()
        request = APIRequestFactory().get("/")
        request.session = {CAS_PROVIDER_SESSION_KEY: "key"}
        adapter = CASAdapter(request)
        service_url = "http://service.url/"
        with patch("plana.apps.users.serializers.cas.CASClient") as CASClient:
            serializer.get_client(request, adapter, service_url)
        CASClient.assert_called_with(
            service_url=service_url,
            server_url=adapter.url,
            version=adapter.version,
            renew=True,
            extra_login_params={},
        )

    @override_settings(CAS_AUTHORIZED_SERVICES=["http://good-service.url"])
    def test_validate_service_is_in_authorized_services(self):
        serializer = CASSerializer()
        validated_service = serializer.validate_service("http://good-service.url")
        self.assertEqual(validated_service, "http://good-service.url")

    @override_settings(CAS_AUTHORIZED_SERVICES=["http://good-service.url"])
    def test_validate_service_not_in_authorized_services_raises_validation_error(self):
        serializer = CASSerializer()
        with self.assertRaises(ValidationError) as ctx:
            validated_service = serializer.validate_service("http://evil-service.url")
        self.assertIn(
            "http://evil-service.url is not a valid service",
            ctx.exception.detail,
        )

    @override_settings(CAS_AUTHORIZED_SERVICES=["http://service.url"])
    @patch("plana.apps.users.serializers.cas.CASClient")
    def test_valid_ticket_adds_user_to_serializer_attributes(self, CASClient):
        user = User.objects.create_user(
            username="username", email="username@unistra.fr"
        )
        group = Group.objects.create(name="Bonjourg")
        user.groups.add(group)
        SocialAccount.objects.create(
            user=user,
            provider=CASProvider.id,
            uid=user.username,
            extra_data={},
        )

        CASClient.return_value.verify_ticket.return_value = ("username", {}, None)
        request = APIRequestFactory().get("/")
        request.session = {}
        view = CASLogin.as_view()
        view.adapter_class = CASAdapter
        serializer = CASSerializer(
            data={"ticket": "CAS-Ticket-123", "service": "http://service.url"},
            context={"view": view, "request": request},
        )
        serializer.is_valid(raise_exception=True)

        self.assertEqual(
            serializer.validated_data["user"],
            user,
        )

    @override_settings(CAS_AUTHORIZED_SERVICES=["http://service.url"])
    def test_view_must_be_present_in_serializer_context(self):
        request = APIRequestFactory().get("/")
        serializer = CASSerializer(
            data={"ticket": "CAS-Ticket-123", "service": "http://service.url"},
            context={"request": request},
        )
        with self.assertRaises(ValidationError) as ctx:
            serializer.is_valid(raise_exception=True)
        self.assertEqual(
            ctx.exception.detail["non_field_errors"][0].code,
            "invalid",
        )

    @override_settings(CAS_AUTHORIZED_SERVICES=["http://service.url"])
    @patch("plana.apps.users.serializers.cas.CASClient")
    def test_a_validation_error_is_raised_if_cas_does_not_validate_the_ticket(
        self, CASClient
    ):
        CASClient.return_value.verify_ticket.return_value = (None, {}, None)
        request = APIRequestFactory().get("/")
        request.session = {}
        view = CASLogin.as_view()
        view.adapter_class = CASAdapter
        serializer = CASSerializer(
            data={"ticket": "CAS-Ticket-123", "service": "http://service.url"},
            context={"view": view, "request": request},
        )
        with self.assertRaises(ValidationError) as ctx:
            serializer.is_valid(raise_exception=True)
        self.assertIn(
            ctx.exception.detail["non_field_errors"][0],
            _("CAS server doesn't validate the ticket"),
        )

    @override_settings(CAS_AUTHORIZED_SERVICES=["http://service.url"])
    @patch("plana.apps.users.serializers.cas.CASClient")
    def test_non_existing_user_is_created(self, CASClient):
        CASClient.return_value.verify_ticket.return_value = (
            "non_existent_user",
            {"mail": "non_existent_user@unistra.fr"},
            None,
        )
        request = APIRequestFactory().get("/")
        request.session = {}
        view = CASLogin.as_view()
        view.adapter_class = CASAdapter
        serializer = CASSerializer(
            data={"ticket": "CAS-Ticket-123", "service": "http://service.url"},
            context={"view": view, "request": request},
        )
        serializer.is_valid(raise_exception=True)

        created_user = User.objects.get(username="non_existent_user")
        self.assertEqual(
            created_user.username,
            "non_existent_user",
        )
        self.assertEqual(
            created_user.email,
            "non_existent_user@unistra.fr",
        )
        self.assertEqual(
            created_user.socialaccount_set.filter(provider=CASProvider.id).count(),
            1,
        )
