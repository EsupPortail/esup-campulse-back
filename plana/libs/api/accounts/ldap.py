from .base import BaseAccountsAPI
from ..ldap_client import first_entry, LdapClient


class LdapAccountsAPI(BaseAccountsAPI, LdapClient):
    @first_entry
    def get_user(self, username):
        return self.search(username=username)
