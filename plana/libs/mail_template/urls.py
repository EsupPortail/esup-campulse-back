from django.urls import path

from . import views

app_name = "mail_template"
urlpatterns = [
    path(
        "<int:pk>/preview",
        views.MailTemplatePreview.as_view(),
        name="mail_template-preview",
    ),
    path(
        "<int:template_id>/vars",
        views.AvailableVarsList.as_view(),
        name="available_vars-list",
    ),
]
