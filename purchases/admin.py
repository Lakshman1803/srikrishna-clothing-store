from django.contrib import admin
from .models import Purchase, PurchaseItem


class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1
    readonly_fields = ("total",)


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ("purchase_invoice_number", "supplier", "date", "grand_total", "payment_status")
    list_filter = ("payment_status", "date")
    search_fields = ("purchase_invoice_number", "supplier__name")
    inlines = [PurchaseItemInline]
