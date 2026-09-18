from django.db import models


class StockMovement(models.Model):
    class Reason(models.TextChoices):
        SALE = "SALE", "Sale"
        PURCHASE = "PURCHASE", "Purchase"
        RETURN = "RETURN", "Return"
        EXCHANGE = "EXCHANGE", "Exchange"
        ADJUSTMENT = "ADJUSTMENT", "Manual Adjustment"

    variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.CASCADE, related_name="stock_movements")
    date = models.DateTimeField(auto_now_add=True)
    previous_stock = models.IntegerField()
    stock_added = models.IntegerField(default=0)
    stock_sold = models.IntegerField(default=0)
    current_stock = models.IntegerField()
    reason = models.CharField(max_length=20, choices=Reason.choices)
    reference = models.CharField(max_length=60, blank=True, help_text="Invoice / Purchase / Return number")
    employee = models.ForeignKey("accounts.User", on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.variant} | {self.reason} | {self.date:%Y-%m-%d}"


def record_stock_movement(variant, stock_added=0, stock_sold=0, reason="ADJUSTMENT", reference="", employee=None):
    """Central helper: applies the delta to the variant and logs the movement atomically."""
    previous = variant.stock_quantity
    variant.stock_quantity = previous + stock_added - stock_sold
    variant.save(update_fields=["stock_quantity"])
    StockMovement.objects.create(
        variant=variant,
        previous_stock=previous,
        stock_added=stock_added,
        stock_sold=stock_sold,
        current_stock=variant.stock_quantity,
        reason=reason,
        reference=reference,
        employee=employee,
    )
    return variant
