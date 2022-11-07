from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth_cas.views import CASAdapter as AllAuthCASAdapter

from django.conf import settings
from django.contrib.auth.models import Group

from .provider import CASProvider

from ..associations.models import Association


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


class CustomUserAdapter(DefaultAccountAdapter):
    def save_user(self, request, user, form, commit=False):
        user = super().save_user(request, user, form, commit)
        data = form.cleaned_data
        user.phone = data.get('phone')

        # Testing if role and association exists in db
        try:
            group = Group.objects.get(name=data.get('role'))
        except Exception as e:
            print(e)
            # TODO : if group does not exist add user in a default one (with the less permissions)
            # Question : add user to group in a different request ?
            user.is_active = False

        user.save()
        user.groups.add(group)
        return user

