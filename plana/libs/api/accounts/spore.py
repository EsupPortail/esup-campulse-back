from .base import BaseAccountsAPI
from ..spore_client import check_status, format_json, SporeClient


class SporeAccountsAPI(BaseAccountsAPI, SporeClient):
    @format_json
    @check_status('spore_accounts')
    def get_user(self, username, *args, **kwargs):
        return self.get_client().get_user(username=username)
