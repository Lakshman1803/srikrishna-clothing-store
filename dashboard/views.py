import csv
import datetime as dt

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, F
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from sales.models import Sale, SaleItem
from customers.models import Customer
from catalog.models import Product, ProductVariant
from expenses.models import Expense
from payments.models import Payment
from purchases.models import Purchase


def _date_range(request):
    """Resolve the selected date filter into (start, end) dates."""
    preset = request.GET.get("range", "today")
    today = timezone.localdate()
    if preset == "yesterday":
        d = today - dt.timedelta(days=1)
        return d, d
    if preset == "this_week":
        start = today - dt.timedelta(days=today.weekday())
        return start, today
    if preset == "this_month":
        return today.replace(day=1), today
    if preset == "last_month":
        first_this = today.replace(day=1)
        last_month_end = first_this - dt.timedelta(days=1)
        return last_month_end.replace(day=1), last_month_end
    if preset == "this_year":
        return today.replace(month=1, day=1), today
    if preset == "custom":
        try:
            start = dt.datetime.strptime(request.GET.get("start", ""), "%Y-%m-%d").date()
            end = dt.datetime.strptime(request.GET.get("end", ""), "%Y-%m-%d").date()
            return start, end
        except ValueError:
            pass
    return today, today


@login_required
def home(request):
    today = timezone.localdate()
    today_sales_qs = Sale.objects.filter(created_at__date=today, status="COMPLETED")
    today_sales = today_sales_qs.aggregate(t=Sum("grand_total"))["t"] or 0
    today_orders = today_sales_qs.count()
    today_expenses = Expense.objects.filter(date=today).aggregate(t=Sum("amount"))["t"] or 0

    today_profit = None
    if request.user.can_view_financials:
        cost = sum(s.total_cost for s in today_sales_qs)
        today_profit = (today_sales - cost) - today_expenses

    total_customers = Customer.objects.count()
    total_products = Product.objects.filter(is_active=True).count()
    total_stock = ProductVariant.objects.aggregate(t=Sum("stock_quantity"))["t"] or 0
    low_stock_products = [p for p in Product.objects.filter(is_active=True) if p.is_low_stock]
    pending_payments = Payment.objects.filter(status__in=["PENDING", "PARTIALLY_PAID"]).aggregate(t=Sum("amount"))["t"] or 0

    # last 7 days sales chart
    labels, data = [], []
    for i in range(6, -1, -1):
        d = today - dt.timedelta(days=i)
        total = Sale.objects.filter(created_at__date=d, status="COMPLETED").aggregate(t=Sum("grand_total"))["t"] or 0
        labels.append(d.strftime("%d %b"))
        data.append(float(total))

    category_sales = (
        SaleItem.objects.filter(sale__status="COMPLETED")
        .values(cat=F("variant__product__category__name"))
        .annotate(total=Sum("line_total"))
        .order_by("-total")
    )

    payment_dist = (
        Payment.objects.filter(status="PAID")
        .values("method").annotate(total=Sum("amount")).order_by("-total")
    )

    context = {
        "today_sales": today_sales,
        "today_orders": today_orders,
        "today_profit": today_profit,
        "today_expenses": today_expenses,
        "total_customers": total_customers,
        "total_products": total_products,
        "total_stock": total_stock,
        "low_stock_products": low_stock_products[:8],
        "low_stock_count": len(low_stock_products),
        "pending_payments": pending_payments,
        "chart_labels": labels,
        "chart_data": data,
        "category_sales": list(category_sales),
        "payment_dist": list(payment_dist),
    }
    return render(request, "dashboard/home.html", context)


@login_required
def reports(request):
    start, end = _date_range(request)
    sales_qs = Sale.objects.filter(created_at__date__gte=start, created_at__date__lte=end, status="COMPLETED")

    total_sales = sales_qs.aggregate(t=Sum("grand_total"))["t"] or 0
    total_orders = sales_qs.count()
    total_gst = sales_qs.aggregate(t=Sum("gst_amount"))["t"] or 0
    total_discount = sales_qs.aggregate(t=Sum("discount_amount"))["t"] or 0
    total_expenses = Expense.objects.filter(date__gte=start, date__lte=end).aggregate(t=Sum("amount"))["t"] or 0

    profit = None
    if request.user.can_view_financials:
        cost = sum(s.total_cost for s in sales_qs)
        profit = (total_sales - total_gst - cost) - total_expenses

    product_sales = (
        SaleItem.objects.filter(sale__in=sales_qs)
        .values(name=F("variant__product__name"), sku=F("variant__product__sku"))
        .annotate(qty=Sum("quantity"), total=Sum("line_total"))
        .order_by("-total")[:15]
    )
    category_sales = (
        SaleItem.objects.filter(sale__in=sales_qs)
        .values(cat=F("variant__product__category__name"))
        .annotate(total=Sum("line_total")).order_by("-total")
    )
    employee_sales = (
        sales_qs.values(name=F("cashier__username")).annotate(total=Sum("grand_total"), orders=Count("id"))
        .order_by("-total")
    )
    low_stock = [p for p in Product.objects.filter(is_active=True) if p.is_low_stock or p.is_out_of_stock]
    purchases_qs = Purchase.objects.filter(date__gte=start, date__lte=end)
    returns_total = sales_qs.model.objects.none()

    context = {
        "start": start, "end": end, "selected_range": request.GET.get("range", "today"),
        "total_sales": total_sales, "total_orders": total_orders, "total_gst": total_gst,
        "total_discount": total_discount, "total_expenses": total_expenses, "profit": profit,
        "product_sales": product_sales, "category_sales": category_sales, "employee_sales": employee_sales,
        "low_stock": low_stock, "purchases_qs": purchases_qs,
    }
    return render(request, "dashboard/reports.html", context)


@login_required
def export_report(request, report_type):
    start, end = _date_range(request)
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = f'attachment; filename="{report_type}_report_{start}_{end}.csv"'
    writer = csv.writer(response)

    if report_type == "sales":
        writer.writerow(["Invoice", "Date", "Customer", "Cashier", "Subtotal", "Discount", "GST", "Grand Total", "Status"])
        for s in Sale.objects.filter(created_at__date__gte=start, created_at__date__lte=end):
            writer.writerow([s.invoice_number, s.created_at.strftime("%Y-%m-%d %H:%M"),
                              s.customer.name if s.customer else "Walk-in", s.cashier, s.subtotal,
                              s.discount_amount, s.gst_amount, s.grand_total, s.status])
    elif report_type == "stock":
        writer.writerow(["Product", "SKU", "Size", "Color", "Barcode", "Stock", "Min Stock"])
        for v in ProductVariant.objects.select_related("product", "size", "color"):
            writer.writerow([v.product.name, v.sku, v.size.label, v.color.name, v.barcode,
                              v.stock_quantity, v.product.minimum_stock])
    elif report_type == "expenses":
        writer.writerow(["Date", "Category", "Description", "Amount", "Payment Method"])
        for e in Expense.objects.filter(date__gte=start, date__lte=end):
            writer.writerow([e.date, e.get_category_display(), e.description, e.amount, e.get_payment_method_display()])
    elif report_type == "purchases":
        writer.writerow(["Purchase Invoice", "Supplier", "Date", "Grand Total", "Payment Status"])
        for p in Purchase.objects.filter(date__gte=start, date__lte=end):
            writer.writerow([p.purchase_invoice_number, p.supplier.name, p.date, p.grand_total, p.payment_status])
    else:
        writer.writerow(["Unknown report type"])

    return response
