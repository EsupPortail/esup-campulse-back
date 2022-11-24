from django.urls import path

from .views.consent import GDPRConsentList

urlpatterns = [
    path("", GDPRConsentList.as_view(), name="gdpr_consent_list"),
]
