from django.db import models


class Supplier(models.Model):
    name = models.CharField(max_length=120)
    company_name = models.CharField(max_length=150, blank=True)
    mobile = models.CharField(max_length=15)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    gst_number = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name

    @property
    def total_purchases(self):
        return self.purchases.count()

    @property
    def total_purchase_amount(self):
        from django.db.models import Sum
        return self.purchases.aggregate(t=Sum("grand_total"))["t"] or 0

    @property
    def pending_payment(self):
        from django.db.models import Sum
        unpaid = self.purchases.exclude(payment_status="PAID")
        total_due = 0
        for p in unpaid:
            total_due += p.balance_due
        return total_due
