import json
import logging
from functools import wraps

import britney
from britney.errors import (
    SporeClientBuildError,
    SporeMethodBuildError,
    SporeMethodCallError,
    SporeMethodStatusError,
)
from britney.middleware import auth, base

from django.conf import settings
from django.utils.translation import gettext_lazy as _


class LogMessageMixin:
    def log(self, level, message='', logger_name=__name__):
        getattr(logging.getLogger(logger_name), level)(message or self.message)


class WSError(LogMessageMixin, Exception):
    def __init__(self, response, message, object_type):
        self.response = response
        self.message = message
        self.object_type = object_type
        self.user_message = _(f'Unable to get information about {object_type}s')


class SporeClient:
    """
    Settings of the Spore client :
        DESCRIPTION_FILE
        BASE_URL
        TOKEN
    """

    __clients = {}

    def get_client(
        self, middlewares=None, reset=False, suffix='json', name='', **kwargs
    ):

        assert hasattr(self, 'api_name'), 'api_name variable missing'

        prefix = self.api_name.upper()
        name = f'{prefix}{f"__{name}" if name else ""}'
        conf = getattr(settings, f'{prefix}_API_CONF')

        if name in self.__clients and not reset:
            return self.__clients[name]

        base_middlewares = (
            (
                'ApiKey',
                {
                    'key_name': 'Authorization',
                    'key_value': f"Token {conf['TOKEN']}",
                },
            ),
        )
        middlewares = base_middlewares + (middlewares or ())

        try:
            client = britney.spyre(
                conf['DESCRIPTION_FILE'],
                base_url=conf['BASE_URL'],
            )
        except (SporeClientBuildError, SporeMethodBuildError) as build_errors:
            logging.getLogger(__name__).error(str(build_errors))
        else:
            for middleware in middlewares:
                kwargs = {}
                if len(middleware) == 2:
                    kwargs = middleware[1]
                predicate = kwargs.pop('predicate', None)
                if predicate:
                    client.enable_if(predicate, middleware[0], **kwargs)
                else:
                    client.enable(middleware[0], **kwargs)

            if suffix:
                client.add_default('format', suffix)

            if not reset:
                self.__clients[name] = client
            return client


def check_status(logger_name=__name__, object_type=''):
    def wrapper(func):
        obj_type = object_type or func.__name__.replace('get_', '').rstrip('s')
        logger = logging.getLogger(logger_name)

        @wraps(func)
        def wrapped(*args, **kwargs):
            logger.debug('Getting %s', obj_type)
            try:
                response = func(*args, **kwargs)
            except SporeMethodStatusError as http_error:
                status = http_error.response.status_code
                if status == 401:
                    message = 'Webservice account can\'t authenticate'
                elif status == 403:
                    message = 'Webservice account needs some authorization'
                elif status >= 500:
                    message = 'Webservice seems to be down'
                else:
                    message = 'Error %s' % http_error.response.reason
                logger.critical(f'{status}: {message}')
                raise WSError(http_error.response, message, obj_type)
            except SporeMethodCallError as method_call_error:
                message = f'Bad function call: {method_call_error.cause}'
                logger.critical(message)
                logger.critical(
                    'Expected values: %s', ', '.join(method_call_error.expected_values)
                )
                raise WSError(None, message, obj_type)
            else:
                logger.debug(response.request.url)
                return response

        return wrapped

    return wrapper


def format_json(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        response = func(*args, **kwargs).content
        return json.loads(response.decode('utf-8')) if response else None

    return wrapper
