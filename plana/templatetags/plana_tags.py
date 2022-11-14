import re

from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def settings_get(name):
    """
    Get a Django setting key.
    """
    try:
        return str(settings.__getattr__(name))
    except Exception:
        return ""


@register.filter(name="uid")
def uid(url):
    """
    Tag used in password_reset_key_message email, represents user id in hex format.
    """
    return re.match(r"^(.*)/(.*)/(.*)/$", url).group(2)


@register.filter(name="token")
def token(url):
    """
    Tag used in password_reset_key_message email, represents token to reset a password.
    """
    return re.match(r"^(.*)/(.*)/(.*)/$", url).group(3)
