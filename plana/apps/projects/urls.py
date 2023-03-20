"""List of URLs directly linked to operations that can be done on projects."""
from django.urls import path

from .views.category import CategoryList

urlpatterns = [
    path("categories", CategoryList.as_view(), name="categories_list"),
]
