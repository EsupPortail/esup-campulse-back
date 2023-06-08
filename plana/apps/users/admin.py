from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AssociationUser, GroupInstitutionCommissionUser, User

admin.site.register(AssociationUser)
admin.site.register(GroupInstitutionCommissionUser)
admin.site.register(User, UserAdmin)
