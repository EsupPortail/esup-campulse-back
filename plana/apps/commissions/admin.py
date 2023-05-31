from django.contrib import admin

from .models import CommissionDate, Fund

admin.site.register(Fund)
admin.site.register(CommissionDate)
