"""Utils file for users app"""
from allauth.account.forms import default_token_generator
from allauth.account.utils import user_pk_to_url_str
from django.conf import settings


def build_password_reset_url(user):
    """Build frontend password reset url for a given user"""
    # Encode user id
    uid = user_pk_to_url_str(user)
    # Generate unique token
    token = default_token_generator.make_token(user)
    # Build frontend url
    base_url = settings.EMAIL_TEMPLATE_FRONTEND_URL.rstrip("/")
    path = settings.EMAIL_TEMPLATE_PASSWORD_RESET_PATH.lstrip("/")

    return f"{base_url}/{path}?uid={uid}&token={token}"
