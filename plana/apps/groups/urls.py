"""List of URLs directly linked to operations that can be done on auth groups."""
from django.urls import path

from .views.group import GroupList

urlpatterns = [
    path("", GroupList.as_view(), name="group_list"),
]
