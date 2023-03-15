"""List of URLs directly linked to operations that can be done on projects."""
from django.urls import path

from .views.category import CategoryList
from .views.project import ProjectRetrieve

urlpatterns = [
    # Project categories urls
    path("categories", CategoryList.as_view(), name="categories_list"),
    # Project urls
    path("<int:pk>", ProjectRetrieve.as_view(), name="project_retrieve"),
]
