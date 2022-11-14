from django import template
from django.conf import settings

register = template.Library()


@register.simple_tag
def settings_get(name):
    try:
        return str(settings.__getattr__(name))
    except Exception:
        return ""
