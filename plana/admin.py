from django.contrib import admin


class SecuredModelAdmin(admin.ModelAdmin):

    def has_module_permission(self, request):
        return super().has_module_permission(request) and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj=obj) and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj=obj) and request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj=obj) and request.user.is_superuser

    def has_add_permission(self, request):
        return super().has_add_permission(request) and request.user.is_superuser


class SecuredInlineAdmin(admin.StackedInline):

    def has_module_permission(self, request):
        return super().has_module_permission(request) and request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return super().has_view_permission(request, obj=obj) and request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return super().has_change_permission(request, obj=obj) and request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return super().has_delete_permission(request, obj=obj) and request.user.is_superuser

    def has_add_permission(self, request, obj):
        return super().has_add_permission(request, obj) and request.user.is_superuser
