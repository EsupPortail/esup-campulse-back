from collections.abc import Generator
from functools import wraps
from typing import Union

from django.conf import settings
from ldap3 import ALL, Connection, Server


def first_entry(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        entries = func(*args, **kwargs)
        if isinstance(entries, list):
            return entries[0] if entries else {}
        return entries or {}

    return wrapper


class LdapClient:
    """
    Settings of the LDAP client :
        HOST
        PORT
        BIND_DN
        PASSWORD
        BASE_DN
        FILTER
        ATTRIBUTES
    """

    @staticmethod
    def decode_value(value: Union[bytes, str]) -> str:
        return value.decode("utf8") if isinstance(value, bytes) else value

    @staticmethod
    def get_mapping(attrs: list[str]) -> dict[str, str]:
        return getattr(settings, 'ACCOUNTS_API_MAPPING', dict(zip(attrs, attrs)))

    def search(self, **kwargs):
        conf = getattr(settings, f'{self.api_name.upper()}_API_CONF')

        results = []
        server = Server(conf['HOST'], port=conf['PORT'], use_ssl=conf['USE_TLS'], get_info=ALL)
        ldap_filter = conf['FILTER'].format(**kwargs)
        mapping = self.get_mapping(conf['ATTRIBUTES'])
        with Connection(server, conf['BIND_DN'], conf['PASSWORD']) as conn:
            conn.search(conf['BASE_DN'], ldap_filter, attributes=conf['ATTRIBUTES'])
            for entry in conn.response:
                result = {}
                attributes = entry['attributes']
                for mapped_attr, ldap_attr in mapping.items():
                    if ldap_val := attributes.get(ldap_attr):
                        value = ldap_val[0] if isinstance(ldap_val, list) and len(ldap_val) else ldap_val
                        result[mapped_attr] = self.decode_value(value)
                results.append(result)
        return results
