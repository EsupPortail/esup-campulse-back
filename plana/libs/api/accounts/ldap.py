from ..ldap_client import LdapClient, first_entry
from .base import BaseAccountsAPI


class LdapAccountsAPI(BaseAccountsAPI, LdapClient):
    @first_entry
    def get_user(self, username):
        return self.search(username=username)
