from django.contrib import admin
from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "sale", "amount", "method", "status", "date")
    list_filter = ("method", "status", "date")
    search_fields = ("transaction_id", "sale__invoice_number", "reference_number")
