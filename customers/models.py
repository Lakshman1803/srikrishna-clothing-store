from django.db import models
from django.core.validators import RegexValidator

mobile_validator = RegexValidator(r"^[6-9]\d{9}$", "Enter a valid 10-digit Indian mobile number.")


class Customer(models.Model):
    name = models.CharField(max_length=120)
    mobile = models.CharField(max_length=10, unique=True, validators=[mobile_validator])
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    loyalty_points = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["-date_joined"]

    def __str__(self):
        return f"{self.name} ({self.mobile})"

    @property
    def total_purchases(self):
        return self.sales.filter(status="COMPLETED").count()

    @property
    def total_amount_spent(self):
        from django.db.models import Sum
        return self.sales.filter(status="COMPLETED").aggregate(t=Sum("grand_total"))["t"] or 0

    @property
    def last_purchase_date(self):
        last = self.sales.filter(status="COMPLETED").order_by("-created_at").first()
        return last.created_at if last else None
