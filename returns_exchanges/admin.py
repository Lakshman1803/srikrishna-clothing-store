from django.contrib import admin
from .models import Return, ReturnItem


class ReturnItemInline(admin.TabularInline):
    model = ReturnItem
    extra = 0


@admin.register(Return)
class ReturnAdmin(admin.ModelAdmin):
    list_display = ("return_number", "sale", "return_type", "resolution", "refund_amount", "date")
    list_filter = ("return_type", "resolution", "date")
    search_fields = ("return_number", "sale__invoice_number")
    inlines = [ReturnItemInline]
