from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Employee / staff account. Role controls permissions across the shop system."""

    class Role(models.TextChoices):
        SUPER_ADMIN = "SUPER_ADMIN", "Super Admin"
        SHOP_OWNER = "SHOP_OWNER", "Shop Owner"
        MANAGER = "MANAGER", "Manager"
        CASHIER = "CASHIER", "Cashier"
        STAFF = "STAFF", "Staff"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CASHIER)
    phone = models.CharField(max_length=15, blank=True)
    is_active_employee = models.BooleanField(default=True)
    date_joined_shop = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_admin_role(self):
        return self.role in (self.Role.SUPER_ADMIN, self.Role.SHOP_OWNER)

    @property
    def can_view_financials(self):
        """Cashiers/staff must not see profit/cost data."""
        return self.role in (self.Role.SUPER_ADMIN, self.Role.SHOP_OWNER, self.Role.MANAGER) or self.is_superuser

    @property
    def can_manage_inventory(self):
        return self.role in (self.Role.SUPER_ADMIN, self.Role.SHOP_OWNER, self.Role.MANAGER) or self.is_superuser

    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"


class AuditLog(models.Model):
    """Records important actions for security/traceability."""

    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_logs")
    action = models.CharField(max_length=255)
    model_name = models.CharField(max_length=100, blank=True)
    object_repr = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.timestamp:%Y-%m-%d %H:%M} - {self.user} - {self.action}"


def log_action(user, action, obj=None, request=None):
    ip = None
    if request is not None:
        ip = request.META.get("REMOTE_ADDR")
    AuditLog.objects.create(
        user=user if getattr(user, "is_authenticated", False) else None,
        action=action,
        model_name=obj.__class__.__name__ if obj is not None else "",
        object_repr=str(obj) if obj is not None else "",
        ip_address=ip,
    )
