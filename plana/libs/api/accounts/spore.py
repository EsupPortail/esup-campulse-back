from ..spore_client import SporeClient, WSError, check_status, format_json
from .base import BaseAccountsAPI


class SporeAccountsAPI(BaseAccountsAPI, SporeClient):
    def get_user(self, username, *args, **kwargs):
        @format_json
        @check_status('external_accounts')
        def get_spore_user():
            return self.get_client().get_user(username=username)

        try:
            return get_spore_user()
        except WSError:
            return {}
