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

        context: Dict[str, Any] = cls.get_context(request, **context_params)
        return render_text(template_data=message_body, data=context)

    @classmethod
    def add_tooltip(cls, var_name: str, content: str):
        text = (
            f"<span style='border-bottom: 1px dotted gray;'>{str(content)}<span title='{str(var_name)}' "
            "class='help help-tooltip help-icon'></span></span>"
        )
        return format_html(text)

    @classmethod
    def get_context(cls, request, user_is, slot_type, local_account, remote):
        today: str = datetime.datetime.today().strftime("%d/%m/%Y")

        # platform_url = Parser.get_platform_url(request)
        platform_url = 'www.google.fr'

        variables = {
            "annee": 2022,
            # "platform_url": platform_url,

            # user
            "prenom": "Dominique",
            "nom": "MARTIN",
            "estlyceen": False,
        }

        context = {key: cls.add_tooltip(key, value) for key, value in variables.items()} 

        # context = {
        #     "annee": cls.add_tooltip("annee", 2022),
        #     "platform_url": cls.add_tooltip("platform_url", platform_url),
        # }

        # # user
        # context.update({
        #     "prenom": cls.add_tooltip("prenom", "Dominique"),
        #     "nom": cls.add_tooltip("nom", "MARTIN"),
        #     "estlyceen": False,
        # })
        # context[user_is] = True

        # # course
        # context.update({
        #     "cours": {
        #         "libelle": cls.add_tooltip("cours.libelle", "Cours n°1"),
        #         "formation": cls.add_tooltip("cours.formation", "Formation n°2"),
        #         "nbplaceslibre": 25,
        #         "type": "TD"
        #     }
        # })

        return context
