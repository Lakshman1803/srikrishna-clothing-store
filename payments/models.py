from django.db import models


class Payment(models.Model):
    class Method(models.TextChoices):
        CASH = "CASH", "Cash"
        UPI = "UPI", "UPI"
        CARD = "CARD", "Card"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"

    class Status(models.TextChoices):
        PAID = "PAID", "Paid"
        PENDING = "PENDING", "Pending"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"
        PARTIAL = "PARTIALLY_PAID", "Partially Paid"

    transaction_id = models.CharField(max_length=40, unique=True)
    sale = models.ForeignKey("sales.Sale", on_delete=models.CASCADE, related_name="payments", null=True, blank=True)
    customer = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=Method.choices)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PAID)
    reference_number = models.CharField(max_length=60, blank=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.transaction_id} - ₹{self.amount} ({self.method})"

    @staticmethod
    def generate_transaction_id():
        import uuid
        return f"TXN{uuid.uuid4().hex[:10].upper()}"
