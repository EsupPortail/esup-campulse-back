"""Generic functions to send emails, and convert "true" and "false" to real booleans."""
import ast
import datetime
import re

import weasyprint
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _
from zxcvbn import zxcvbn


def check_valid_password(password):
    """Check password standard rules and zxcvbn rules."""

    messages = []
    min_length = 8
    if len(password) < min_length:
        messages += [_(f"Password too short (at least {min_length} chars).")]

    if not re.search("[a-z]+", password):
        messages += [_("Password should contain at least one lowercase character.")]

    if not re.search("[A-Z]+", password):
        messages += [_("Password should contain at least one uppercase character.")]

    if not re.search("[0-9]+", password):
        messages += [_("Password should contain at least one digit.")]

    if not re.search("[!-/:-@[-`{-~]", password):
        messages += [
            _(
                "Password should contain at least one special char ( / * - + = . , ; : ! ? & \" \' ( ) _ [ ] { } @ % # $ < > )."
            )
        ]

    password_result = zxcvbn(password)
    if password_result["score"] < 4 and len(messages) == 0:
        messages += [_("Password is still too weak, please add some characters.")]
    messages += password_result["feedback"]["suggestions"]

    return_messages = {
        "valid": len(messages) == 0,
        "messages": messages,
    }
    return return_messages


def _listify(x):
    return list(filter(None, set(x if isinstance(x, (list, tuple, set)) else [x])))


def send_mail(
    to_, subject, message, from_='', attachments=None, has_html=True, **kwargs
):
    # Listify recipient address
    to_ = _listify(to_)
    from_ = from_ or settings.DEFAULT_FROM_EMAIL

    mail = EmailMultiAlternatives(subject, message, from_, to_, **kwargs)
    if has_html:
        mail.attach_alternative(message, "text/html")

    # Attachments
    attachments = attachments or ()
    for att in attachments:
        with att.storage.open(f'{att.filepath}/{att.filename}', 'rb') as file:
            content = file.read()
            mail.attach(att.filename, content, att.mimetype)

    mail.send()


def to_bool(attr):
    """Translate strings like "true"/"false" into boolean."""

    if isinstance(attr, bool):
        return attr
    if isinstance(attr, str):
        return ast.literal_eval(attr.capitalize())


def valid_date_format(date):
    date_format = "%Y-%m-%d"
    try:
        datetime.datetime.strptime(date, date_format)
    except ValueError:
        return False
    return True


def generate_pdf(filename, dict_data, type_doc, base_url):
    types_and_templates = {
        "association_charter_summary": "./pdf_exports/association_charter_summary.html",
        "project_summary": "./pdf_exports/project_summary.html",
        "project_review_summary": "./pdf_exports/project_review_summary.html",
    }
    html = render_to_string(types_and_templates[type_doc], dict_data)
    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'Content-Disposition: attachment; filename="{slugify(filename)}.pdf"'
    weasyprint.HTML(string=html, base_url=base_url).write_pdf(response)
    return response
