from django.conf import settings


class CASProvider:
    """Fake provider class to keep comptaibility with existing querysets"""

    # ID configured in settings (default to "cas")
    id = getattr(settings, "CAS_ID", "cas")
