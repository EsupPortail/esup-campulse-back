from django.urls import path

from . import views


app_name = "mail_template"
urlpatterns = [
    path("<int:pk>/preview", views.MailTemplatePreviewAPI.as_view(), name="mail_template-preview"),
    path("<int:template_id>/vars", views.ajax_get_available_vars, name="GetAvailableVars",),
]
