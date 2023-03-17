"""List of URLs directly linked to operations that can be done on projects."""
from django.urls import path

from .views.category import CategoryListCreate
from .views.project import ProjectListCreate, ProjectRetrieve
from .views.project_category import ProjectCategoryDestroy

urlpatterns = [
    # Project categories urls
    path(
        "categories",
        CategoryListCreate.as_view(),
        name="project_categories_list_create",
    ),
    # Project category links urls
    path(
        "<int:project_id>/category/<int:category_id>",
        ProjectCategoryDestroy.as_view(),
        name="project_category_destroy",
    ),
    # Project urls
    path("", ProjectListCreate.as_view(), name="project_list_create"),
    path("<int:pk>", ProjectRetrieve.as_view(), name="project_retrieve"),
]
