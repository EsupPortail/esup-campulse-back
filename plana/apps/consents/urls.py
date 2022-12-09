"""
List of URLs directly linked to operations that can be done on GDPR consents.
"""
from django.urls import path

from .views.consent import GDPRConsentList

urlpatterns = [
    path("", GDPRConsentList.as_view(), name="gdpr_consent_list"),
]
