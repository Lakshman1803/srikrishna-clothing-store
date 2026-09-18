from django.contrib import admin
from .models import StockMovement


@admin.register(StockMovement)
class StockMovementAdmin(admin.ModelAdmin):
    list_display = ("date", "variant", "reason", "previous_stock", "stock_added", "stock_sold",
                     "current_stock", "reference", "employee")
    list_filter = ("reason", "date")
    search_fields = ("variant__sku", "variant__barcode", "reference")
    date_hierarchy = "date"
