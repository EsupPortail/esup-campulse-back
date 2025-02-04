"""Describes the used CAS service and the fields retrieved from it."""

from allauth.socialaccount.providers.base import ProviderAccount
from allauth_cas.providers import CASProvider as AllAuthCASProvider
from django.conf import settings


class CASAccount(ProviderAccount):
    """Default CAS Account."""


class CASProvider(AllAuthCASProvider):
    """The CASProvider subclass defines how to process data returned by the CAS server."""

    id = settings.CAS_ID
    name = settings.CAS_NAME
    account_class = CASAccount
    uses_apps = False

    def extract_uid(self, data) -> str:
        uid = super().extract_uid(data)
        return uid.lower()

    def extract_common_fields(self, data) -> dict[str, str]:
        uid, extra = data
        fields = {
            "username": uid,
            "email": extra.get(settings.CAS_ATTRIBUTES_NAMES["email"], ""),
            "first_name": extra.get(settings.CAS_ATTRIBUTES_NAMES["first_name"], ""),
            "last_name": extra.get(settings.CAS_ATTRIBUTES_NAMES["last_name"], ""),
        }
        return fields


provider_classes = [CASProvider]
