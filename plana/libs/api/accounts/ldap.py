from ..ldap_client import LdapClient, first_entry
from .base import BaseAccountsAPI


class LdapAccountsAPI(BaseAccountsAPI, LdapClient):
    def list_users(self, *args, **kwargs):
        return self.search(**kwargs)
