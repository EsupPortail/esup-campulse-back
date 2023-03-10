from ..spore_client import SporeClient, WSError, check_status, format_json
from .base import BaseAccountsAPI


class SporeAccountsAPI(BaseAccountsAPI, SporeClient):
    def list_users(self, *args, **kwargs):
        @format_json
        @check_status('external_accounts')
        def list_spore_users():
            params = {'establishment': 'uds'}
            return self.get_client().list_accounts(**params, **kwargs)

        try:
            return list_spore_users()
        except WSError:
            return {}
