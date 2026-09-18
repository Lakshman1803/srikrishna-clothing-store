import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404

from inventory.models import record_stock_movement
from sales.models import Sale, SaleItem
from .models import Return, ReturnItem


@login_required
def return_list(request):
    returns = Return.objects.select_related("sale").all()
    return render(request, "returns_exchanges/return_list.html", {"returns": returns[:200]})


@login_required
def find_invoice(request):
    invoice_number = request.GET.get("invoice", "").strip()
    try:
        sale = Sale.objects.get(invoice_number__iexact=invoice_number)
    except Sale.DoesNotExist:
        return JsonResponse({"found": False})
    items = [{
        "sale_item_id": i.id, "product": i.variant.product.name, "size": i.variant.size.label,
        "color": i.variant.color.name, "quantity": i.quantity, "unit_price": str(i.unit_price),
    } for i in sale.items.all()]
    return JsonResponse({"found": True, "invoice_number": sale.invoice_number, "customer": sale.customer.name if sale.customer else "Walk-in", "items": items})


@login_required
@transaction.atomic
def return_create(request):
    if request.method == "POST":
        invoice_number = request.POST.get("invoice_number")
        return_type = request.POST.get("return_type", "RETURN")
        resolution = request.POST.get("resolution", "REFUND")
        reason = request.POST.get("reason", "")
        try:
            selected_items = json.loads(request.POST.get("items", "[]"))
        except json.JSONDecodeError:
            selected_items = []

        sale = get_object_or_404(Sale, invoice_number=invoice_number)
        if not selected_items:
            messages.error(request, "Select at least one item to return.")
            return redirect("returns_exchanges:return_create")

        last = Return.objects.order_by("-id").first()
        next_num = (last.id + 1) if last else 1
        ret = Return.objects.create(
            return_number=f"RET-{next_num:06d}", sale=sale, return_type=return_type,
            resolution=resolution, reason=reason, processed_by=request.user,
        )
        refund_total = Decimal("0")
        for it in selected_items:
            sale_item = get_object_or_404(SaleItem, pk=it["sale_item_id"], sale=sale)
            qty = int(it["quantity"])
            ReturnItem.objects.create(ret=ret, original_sale_item=sale_item, quantity=qty)
            # Return goes back to stock
            record_stock_movement(sale_item.variant, stock_added=qty, reason="RETURN", reference=ret.return_number, employee=request.user)
            refund_total += (sale_item.unit_price * qty)
        ret.refund_amount = refund_total
        ret.save(update_fields=["refund_amount"])
        messages.success(request, f"{ret.get_return_type_display()} {ret.return_number} processed. Inventory updated.")
        return redirect("returns_exchanges:return_list")

    return render(request, "returns_exchanges/return_form.html")
