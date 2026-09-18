import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from catalog.models import ProductVariant
from inventory.models import record_stock_movement
from suppliers.models import Supplier
from .models import Purchase, PurchaseItem


@login_required
def purchase_list(request):
    purchases = Purchase.objects.select_related("supplier").all()
    return render(request, "purchases/purchase_list.html", {"purchases": purchases[:200]})


@login_required
@transaction.atomic
def purchase_create(request):
    if request.method == "POST":
        supplier_id = request.POST.get("supplier")
        date = request.POST.get("date")
        payment_status = request.POST.get("payment_status", "PENDING")
        amount_paid = Decimal(request.POST.get("amount_paid", "0") or 0)
        try:
            items = json.loads(request.POST.get("items", "[]"))
        except json.JSONDecodeError:
            items = []

        if not items:
            messages.error(request, "Add at least one item to the purchase.")
            return redirect("purchases:purchase_create")

        supplier = get_object_or_404(Supplier, pk=supplier_id)
        last = Purchase.objects.order_by("-id").first()
        next_num = (last.id + 1) if last else 1
        purchase = Purchase.objects.create(
            purchase_invoice_number=f"PUR-{next_num:06d}", supplier=supplier, date=date,
            payment_status=payment_status, amount_paid=amount_paid, created_by=request.user,
        )
        for it in items:
            variant = get_object_or_404(ProductVariant, pk=it["variant_id"])
            qty = int(it["quantity"])
            price = Decimal(str(it["purchase_price"]))
            gst = Decimal(str(it.get("gst_percent", 0)))
            PurchaseItem.objects.create(purchase=purchase, variant=variant, quantity=qty, purchase_price=price, gst_percent=gst)
            record_stock_movement(variant, stock_added=qty, reason="PURCHASE", reference=purchase.purchase_invoice_number, employee=request.user)
        purchase.recalc_total()
        messages.success(request, f"Purchase {purchase.purchase_invoice_number} recorded and stock updated.")
        return redirect("purchases:purchase_detail", pk=purchase.pk)

    suppliers = Supplier.objects.all()
    variants = ProductVariant.objects.select_related("product", "size", "color")[:500]
    return render(request, "purchases/purchase_form.html", {"suppliers": suppliers, "variants": variants})


@login_required
def purchase_detail(request, pk):
    purchase = get_object_or_404(Purchase, pk=pk)
    return render(request, "purchases/purchase_detail.html", {"purchase": purchase})
