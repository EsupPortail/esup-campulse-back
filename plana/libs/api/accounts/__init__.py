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


def get_client():
    client_path = f"plana.libs.api.accounts.{settings.ACCOUNTS_API_CLIENT.lower()}.{settings.ACCOUNTS_API_CLIENT}AccountsAPI"
    mod, package = client_path.rsplit('.', 1)
    client_class = getattr(import_module(mod), package)
    return client_class()
