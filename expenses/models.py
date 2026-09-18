from django.db import models
from django.conf import settings


class Expense(models.Model):
    class Category(models.TextChoices):
        RENT = "RENT", "Rent"
        ELECTRICITY = "ELECTRICITY", "Electricity"
        SALARY = "SALARY", "Salary"
        TRANSPORT = "TRANSPORT", "Transport"
        INTERNET = "INTERNET", "Internet"
        MAINTENANCE = "MAINTENANCE", "Maintenance"
        MARKETING = "MARKETING", "Marketing"
        PACKAGING = "PACKAGING", "Packaging"
        MISC = "MISC", "Miscellaneous"

    class PaymentMethod(models.TextChoices):
        CASH = "CASH", "Cash"
        UPI = "UPI", "UPI"
        CARD = "CARD", "Card"
        BANK_TRANSFER = "BANK_TRANSFER", "Bank Transfer"

    date = models.DateField()
    category = models.CharField(max_length=20, choices=Category.choices)
    description = models.CharField(max_length=255, blank=True)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices, default=PaymentMethod.CASH)
    employee = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.get_category_display()} - ₹{self.amount} ({self.date})"
