from django.contrib import admin

from .models import Commission, Fund

admin.site.register(Fund)
admin.site.register(Commission)
