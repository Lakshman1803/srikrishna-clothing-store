from django.contrib import admin
from .models import Customer


@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ("name", "mobile", "email", "total_purchases", "total_amount_spent", "loyalty_points", "date_joined")
    search_fields = ("name", "mobile", "email")
    list_filter = ("date_joined",)
