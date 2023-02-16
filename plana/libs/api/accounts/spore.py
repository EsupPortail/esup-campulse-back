from .base import BaseAccountsAPI
from ..spore_client import check_status, format_json, SporeClient, WSError


class SporeAccountsAPI(BaseAccountsAPI, SporeClient):
    def get_user(self, username, *args, **kwargs):
        @format_json
        @check_status('spore_accounts')
        def get_spore_user():
            return self.get_client().get_user(username=username)

        try:
            return get_spore_user()
        except WSError:
            return {}
