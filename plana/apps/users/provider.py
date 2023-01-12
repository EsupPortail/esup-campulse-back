"""
Describes the used CAS service and the fields retrieved from it.
"""
from allauth.socialaccount.providers.base import ProviderAccount
from allauth_cas.providers import CASProvider as AllAuthCASProvider


class CASAccount(ProviderAccount):
    """
    Default CAS Account.
    """

    pass


class CASProvider(AllAuthCASProvider):
    """
    The CASProvider subclass defines how to process data returned by the CAS server.
    """

    id = "cas"
    name = "CAS Unistra"
    account_class = CASAccount

    def extract_uid(self, data) -> str:
        uid = super().extract_uid(data)
        return uid.lower()

    def extract_common_fields(self, data) -> dict[str, str]:
        uid, extra = data
        fields = {
            "username": uid,
            "email": extra.get("mail", ""),
            "first_name": extra.get("first_name", ""),
            "last_name": extra.get("last_name", ""),
        }
        return fields


provider_classes = [CASProvider]
