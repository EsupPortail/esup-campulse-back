"""List of URLs directly linked to operations that can be done on projects."""
from django.urls import path

from .views.category import CategoryList
from .views.project import ProjectListCreate, ProjectRetrieve

urlpatterns = [
    # Project categories urls
    path("categories", CategoryList.as_view(), name="categories_list"),
    # Project urls
    path("", ProjectListCreate.as_view(), name="project_list_create"),
    path("<int:pk>", ProjectRetrieve.as_view(), name="project_retrieve"),
]
