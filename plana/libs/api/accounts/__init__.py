try:
    from .ldap import LdapAccountsAPI
except ImportError:
    pass

try:
    from .spore import SporeAccountsAPI
except ImportError:
    pass

from importlib import import_module

from django.conf import settings


def _get_client():
    conf = settings.ACCOUNTS_API_CONF
    mod, package = settings.ACCOUNTS_API_CLIENT.rsplit('.', 1)
    return getattr(import_module(mod), package)


Client = _get_client()
