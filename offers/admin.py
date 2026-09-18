from django.contrib import admin
from .models import Offer, Coupon


@admin.register(Offer)
class OfferAdmin(admin.ModelAdmin):
    list_display = ("title", "offer_type", "discount_value", "start_date", "end_date", "is_active")
    list_filter = ("offer_type", "is_active")
    filter_horizontal = ("categories",)


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ("code", "offer", "max_uses", "times_used")
    search_fields = ("code",)
