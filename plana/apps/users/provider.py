from allauth.socialaccount.providers.base import ProviderAccount
from allauth_cas.providers import CASProvider as AllAuthCASProvider


class CASAccount(ProviderAccount):
    pass


class CASProvider(AllAuthCASProvider):
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
            # "affiliation": extra.get("affiliation"),
            # "top_unit_code": extra.get("top_unit_code"),
            # "academic_year": extra.get("academic_year"),
        }
        return fields


provider_classes = [CASProvider]