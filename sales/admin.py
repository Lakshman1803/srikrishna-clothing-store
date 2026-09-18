from django.contrib import admin
from .models import Sale, SaleItem


class SaleItemInline(admin.TabularInline):
    model = SaleItem
    extra = 0
    readonly_fields = ("line_total",)


@admin.register(Sale)
class SaleAdmin(admin.ModelAdmin):
    list_display = ("invoice_number", "customer", "cashier", "grand_total", "status", "created_at")
    list_filter = ("status", "created_at")
    search_fields = ("invoice_number", "customer__name", "customer__mobile")
    inlines = [SaleItemInline]
    date_hierarchy = "created_at"
