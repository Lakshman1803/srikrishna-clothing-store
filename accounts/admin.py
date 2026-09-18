from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, AuditLog


@admin.register(User)
class SriKrishnaUserAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "role", "phone", "is_active_employee", "is_staff")
    list_filter = ("role", "is_active_employee", "is_staff")
    fieldsets = UserAdmin.fieldsets + (
        ("Shop Employee Info", {"fields": ("role", "phone", "is_active_employee", "date_joined_shop")}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Shop Employee Info", {"fields": ("role", "phone", "is_active_employee", "date_joined_shop")}),
    )


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "user", "action", "model_name", "object_repr", "ip_address")
    list_filter = ("action", "model_name")
    search_fields = ("user__username", "action", "object_repr")
    readonly_fields = [f.name for f in AuditLog._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False
