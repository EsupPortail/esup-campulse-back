"""
Generic functions to send emails, and convert "true" and "false" to real booleans.
"""
import ast

from django.conf import settings
from django.core.mail import EmailMultiAlternatives


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
    """
    Used to translate strings like "true"/"false" into boolean
    """
    if isinstance(attr, bool):
        return attr
    if isinstance(attr, str):
        return ast.literal_eval(attr.capitalize())
