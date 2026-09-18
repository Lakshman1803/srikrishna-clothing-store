from django.contrib import admin
from .models import Supplier


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ("name", "company_name", "mobile", "gst_number", "total_purchases", "pending_payment")
    search_fields = ("name", "company_name", "mobile", "gst_number")
