from django.urls import path

from .views.group import GroupList

urlpatterns = [
    path("", GroupList.as_view(), name="group_list"),
]
