from django.contrib import admin

from .models import Content, Logo


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = ["code", "label"]
    search_fields = ["code", "label", "title", "header", "body", "footer", "aside"]


@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = ["acronym", "title", "url", "visible"]
    list_filter = ["visible"]
    search_fields = ["acronym", "title"]
