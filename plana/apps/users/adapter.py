from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth_cas.views import CASAdapter as AllAuthCASAdapter

from django.conf import settings

from .provider import CASProvider


class PlanAAdapter(DefaultAccountAdapter):
    pass


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    pass


class CASAdapter(AllAuthCASAdapter):
    provider_id = CASProvider.id
    url = settings.CAS_SERVER
    version = settings.CAS_VERSION

    def get_provider(self, request):
        return self.provider
