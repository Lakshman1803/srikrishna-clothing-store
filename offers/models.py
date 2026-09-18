from django.db import models


class Offer(models.Model):
    class OfferType(models.TextChoices):
        PERCENTAGE = "PERCENTAGE", "Percentage Discount"
        FIXED = "FIXED", "Fixed Amount Discount"
        BOGO = "BOGO", "Buy 1 Get 1"
        FESTIVAL = "FESTIVAL", "Festival Offer"

    title = models.CharField(max_length=150)
    offer_type = models.CharField(max_length=20, choices=OfferType.choices)
    description = models.TextField(blank=True)
    categories = models.ManyToManyField("catalog.Category", blank=True, related_name="offers")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, help_text="% or ₹ depending on offer type")
    minimum_purchase = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    maximum_discount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-start_date"]

    def __str__(self):
        return self.title

    @property
    def is_currently_running(self):
        from django.utils import timezone
        today = timezone.localdate()
        return self.is_active and self.start_date <= today <= self.end_date


class Coupon(models.Model):
    code = models.CharField(max_length=30, unique=True)
    offer = models.ForeignKey(Offer, on_delete=models.CASCADE, related_name="coupons")
    max_uses = models.PositiveIntegerField(default=100)
    times_used = models.PositiveIntegerField(default=0)
    customer_specific = models.ForeignKey("customers.Customer", on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.code

    @property
    def is_valid(self):
        return self.offer.is_currently_running and self.times_used < self.max_uses
