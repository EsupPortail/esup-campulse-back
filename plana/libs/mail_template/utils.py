import datetime
from functools import wraps
from typing import Any, Dict, Optional, List

from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.template import engines
from django.utils.html import format_html

from .models import MailTemplateVar


User = get_user_model()


def is_ajax_request(view_func):
    """
    Check if the request is ajax
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.is_ajax():
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("<h1>Forbidden</h1>You do not have \
            permission to access this page.")
    return wrapper


def render_text(template_data: str, data: Dict[str, Any]) -> str:
    """
    Render a text base on jinja2 engine
    :param template_data:
    :param data:
    :return:
    """
    django_engine = engines["django"]
    template = django_engine.from_string(template_data)
    return template.render(context=data)


def parser(message_body, available_vars=None, user=None, request=None, **kwargs):
    return Parser.parser(
        message_body=message_body,
        available_vars=available_vars,
        user=user,
        request=request,
        **kwargs
    )


def parser_faker(message_body, context_params, available_vars=None, user=None, request=None, **kwargs):
    return ParserFaker.parser(
        message_body=message_body,
        context_params=context_params,
        available_vars=available_vars,
        user=user,
        request=request,
        **kwargs
    )


class ParserFaker:
    @classmethod
    def parser(cls, message_body: str, available_vars: Optional[List[MailTemplateVar]], context_params: Dict[str, Any],
               user: Optional[User] = None, request=None, **kwargs) -> str:

        context = cls.get_context(request, available_vars=available_vars, extra_variables=context_params)
        return render_text(template_data=message_body, data=context)

    @classmethod
    def add_tooltip(cls, var_name: str, content: str):
        text = (
            f"<span style='border-bottom: 1px dotted gray;'>{str(content)}<span title='{str(var_name)}' "
            "class='help help-tooltip help-icon'></span></span>"
        )
        return format_html(text)

    @classmethod
    def get_context(cls, request, available_vars=None, extra_variables=None):
        # Get mono-value fakevars
        variables = {}
        for template_var in available_vars:
            if (len(fakevars := template_var.fakevars) == 1):
                variables[template_var.name] = fakevars[0].value

        context = {key: cls.add_tooltip(key, value) for key, value in variables.items()}
        context.update(extra_variables or {})
        return context
