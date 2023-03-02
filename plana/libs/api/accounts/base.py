import abc


class BaseAccountsAPI(metaclass=abc.ABCMeta):

    api_name = 'accounts'

    @abc.abstractmethod
    def get_user(self, *args, **kwargs):
        pass
