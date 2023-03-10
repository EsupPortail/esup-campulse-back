import abc


class BaseAccountsAPI(metaclass=abc.ABCMeta):

    api_name = 'accounts'

    @abc.abstractmethod
    def list_users(self, *args, **kwargs):
        pass
