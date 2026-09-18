from django.db import models
from django.conf import settings


class Return(models.Model):
    class ReturnType(models.TextChoices):
        RETURN = "RETURN", "Return"
        EXCHANGE = "EXCHANGE", "Exchange"

    class Resolution(models.TextChoices):
        REFUND = "REFUND", "Refund"
        STORE_CREDIT = "STORE_CREDIT", "Store Credit"
        EXCHANGED = "EXCHANGED", "Exchanged for another item"

    return_number = models.CharField(max_length=30, unique=True)
    sale = models.ForeignKey("sales.Sale", on_delete=models.CASCADE, related_name="returns")
    return_type = models.CharField(max_length=10, choices=ReturnType.choices, default=ReturnType.RETURN)
    resolution = models.CharField(max_length=20, choices=Resolution.choices, default=Resolution.REFUND)
    reason = models.TextField()
    processed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    refund_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return self.return_number


class ReturnItem(models.Model):
    ret = models.ForeignKey(Return, on_delete=models.CASCADE, related_name="items")
    original_sale_item = models.ForeignKey("sales.SaleItem", on_delete=models.PROTECT, related_name="return_items")
    quantity = models.PositiveIntegerField()
    exchange_variant = models.ForeignKey("catalog.ProductVariant", on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name="exchange_return_items",
                                          help_text="If this is an exchange, the new variant given to customer")

    def __str__(self):
        return f"{self.original_sale_item.variant} x{self.quantity}"
