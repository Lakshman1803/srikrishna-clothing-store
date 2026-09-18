from decimal import Decimal
from django.db import models
from django.conf import settings


class Sale(models.Model):
    class Status(models.TextChoices):
        COMPLETED = "COMPLETED", "Completed"
        HELD = "HELD", "Held"
        CANCELLED = "CANCELLED", "Cancelled"

    invoice_number = models.CharField(max_length=30, unique=True)
    customer = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, blank=True, related_name="sales")
    cashier = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name="sales_billed")
    subtotal = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    gst_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    coupon_code = models.CharField(max_length=30, blank=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.COMPLETED)
    loyalty_points_earned = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.invoice_number

    @staticmethod
    def generate_invoice_number():
        from shopsettings.models import ShopSettings
        settings_obj = ShopSettings.get_solo()
        prefix = settings_obj.invoice_prefix or "SK"
        last = Sale.objects.order_by("-id").first()
        next_id = (last.id + 1) if last else 1
        return f"{prefix}-{next_id:06d}"

    @property
    def total_cost(self):
        """Sum of purchase price * qty across items - for profit calc, hidden from cashiers in UI."""
        return sum(item.quantity * item.variant.product.purchase_price for item in self.items.all())

    @property
    def gross_profit(self):
        return self.grand_total - self.gst_amount - self.total_cost

    @property
    def amount_paid(self):
        return sum(p.amount for p in self.payments.filter(status="PAID"))

    @property
    def balance_due(self):
        return self.grand_total - self.amount_paid


class SaleItem(models.Model):
    sale = models.ForeignKey(Sale, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.PROTECT, related_name="sale_items")
    quantity = models.PositiveIntegerField(default=1)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    line_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.variant} x{self.quantity}"

    def save(self, *args, **kwargs):
        base = (self.unit_price * self.quantity) - self.discount_amount
        gst = base * (self.gst_percent / Decimal(100))
        self.line_total = round(base + gst, 2)
        super().save(*args, **kwargs)
