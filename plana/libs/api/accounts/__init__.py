from .ldap import LdapAccountsAPI
from .spore import SporeAccountsAPI

from importlib import import_module

from django.conf import settings


def _get_client():
    conf = settings.ACCOUNTS_API_CONF
    mod, package = settings.ACCOUNTS_API_CLIENT.rsplit('.', 1)
    return getattr(import_module(mod), package)


Client = _get_client()
