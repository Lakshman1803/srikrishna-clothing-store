from django.db import models
from django.conf import settings


class Purchase(models.Model):
    class PaymentStatus(models.TextChoices):
        PAID = "PAID", "Paid"
        PENDING = "PENDING", "Pending"
        PARTIAL = "PARTIALLY_PAID", "Partially Paid"

    purchase_invoice_number = models.CharField(max_length=40, unique=True)
    supplier = models.ForeignKey("suppliers.Supplier", on_delete=models.PROTECT, related_name="purchases")
    date = models.DateField()
    payment_status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    grand_total = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.purchase_invoice_number

    @property
    def balance_due(self):
        return self.grand_total - self.amount_paid

    def recalc_total(self):
        self.grand_total = sum(i.total for i in self.items.all())
        self.save(update_fields=["grand_total"])


class PurchaseItem(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="items")
    variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.PROTECT, related_name="purchase_items")
    quantity = models.PositiveIntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    gst_percent = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=12, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        from decimal import Decimal
        base = self.purchase_price * self.quantity
        gst = base * (self.gst_percent / Decimal(100))
        self.total = round(base + gst, 2)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.variant} x{self.quantity}"
