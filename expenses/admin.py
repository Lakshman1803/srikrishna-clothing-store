from django.contrib import admin
from .models import Expense


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ("date", "category", "amount", "payment_method", "employee")
    list_filter = ("category", "payment_method", "date")
    search_fields = ("description",)
