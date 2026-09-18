from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Sum, Q
from django.shortcuts import render, redirect, get_object_or_404

from catalog.models import Product, ProductVariant, Category
from .models import StockMovement, record_stock_movement


@login_required
def stock_list(request):
    variants = ProductVariant.objects.select_related("product", "size", "color", "product__category").all()
    q = request.GET.get("q", "").strip()
    category = request.GET.get("category", "")
    status = request.GET.get("status", "")
    if q:
        variants = variants.filter(Q(product__name__icontains=q) | Q(sku__icontains=q) | Q(barcode__icontains=q))
    if category:
        variants = variants.filter(product__category_id=category)
    if status == "low":
        variants = [v for v in variants if v.is_low_stock]
    elif status == "out":
        variants = [v for v in variants if v.stock_quantity <= 0]

    total_products = Product.objects.filter(is_active=True).count()
    total_stock = ProductVariant.objects.aggregate(t=Sum("stock_quantity"))["t"] or 0
    low_stock = len([p for p in Product.objects.filter(is_active=True) if p.is_low_stock])
    out_of_stock = len([p for p in Product.objects.filter(is_active=True) if p.is_out_of_stock])

    context = {
        "variants": variants if isinstance(variants, list) else variants[:300],
        "categories": Category.objects.all(), "q": q, "selected_category": category, "selected_status": status,
        "total_products": total_products, "total_stock": total_stock, "low_stock": low_stock, "out_of_stock": out_of_stock,
    }
    return render(request, "inventory/stock_list.html", context)


@login_required
def movement_list(request):
    movements = StockMovement.objects.select_related("variant__product", "employee").all()[:300]
    return render(request, "inventory/movement_list.html", {"movements": movements})


@login_required
@user_passes_test(lambda u: u.can_manage_inventory)
def adjust_stock(request, variant_id):
    variant = get_object_or_404(ProductVariant, pk=variant_id)
    if request.method == "POST":
        try:
            new_qty = int(request.POST.get("new_quantity"))
            diff = new_qty - variant.stock_quantity
            if diff >= 0:
                record_stock_movement(variant, stock_added=diff, reason="ADJUSTMENT", reference="Manual adjustment", employee=request.user)
            else:
                record_stock_movement(variant, stock_sold=-diff, reason="ADJUSTMENT", reference="Manual adjustment", employee=request.user)
            messages.success(request, f"Stock for {variant} updated to {new_qty}.")
        except (TypeError, ValueError):
            messages.error(request, "Invalid quantity.")
    return redirect("inventory:stock_list")
