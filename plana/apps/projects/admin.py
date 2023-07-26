from django.contrib import admin

from .models import (
    Category,
    Project,
    ProjectCategory,
    ProjectComment,
    ProjectCommissionFund,
)

admin.site.register(Category)
admin.site.register(Project)
admin.site.register(ProjectCategory)
admin.site.register(ProjectComment)
admin.site.register(ProjectCommissionFund)
