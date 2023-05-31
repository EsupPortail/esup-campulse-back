from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import AssociationUser, GroupInstitutionFundUser, User

admin.site.register(AssociationUser)
admin.site.register(GroupInstitutionFundUser)
admin.site.register(User, UserAdmin)
