from django.contrib import admin

from .models import Content, Logo


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    list_display = [
        "code",
        "label",
    ]


@admin.register(Logo)
class LogoAdmin(admin.ModelAdmin):
    list_display = [
        "acronym",
        "title",
        "url",
        "visible",
    ]
