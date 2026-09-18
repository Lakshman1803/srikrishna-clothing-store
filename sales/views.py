import json
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse

from catalog.models import ProductVariant
from customers.models import Customer, mobile_validator
from inventory.models import record_stock_movement
from payments.models import Payment
from shopsettings.models import ShopSettings
from .models import Sale, SaleItem


@login_required
def pos(request):
    settings_obj = ShopSettings.get_solo()
    return render(request, "sales/pos.html", {"shop": settings_obj})


@login_required
def search_product(request):
    """AJAX: search by name / SKU / barcode; returns matching variants with stock."""
    q = request.GET.get("q", "").strip()
    if not q:
        return JsonResponse({"results": []})
    variants = ProductVariant.objects.select_related("product", "size", "color").filter(
        Q(barcode__iexact=q) | Q(sku__icontains=q) | Q(product__name__icontains=q) | Q(product__sku__icontains=q)
    ).filter(product__is_active=True)[:20]
    results = []
    for v in variants:
        results.append({
            "variant_id": v.id,
            "product_name": v.product.name,
            "size": v.size.label,
            "color": v.color.name,
            "sku": v.sku,
            "barcode": v.barcode,
            "price": str(v.product.effective_price),
            "mrp": str(v.product.mrp),
            "gst_percent": str(v.product.gst_percent),
            "stock": v.stock_quantity,
            "image": v.product.image.url if v.product.image else "",
        })
    return JsonResponse({"results": results})


@login_required
@transaction.atomic
def checkout(request):
    if request.method != "POST":
        return redirect("sales:pos")

    try:
        cart = json.loads(request.POST.get("cart", "[]"))
    except json.JSONDecodeError:
        cart = []

    if not cart:
        messages.error(request, "Cart is empty.")
        return redirect("sales:pos")

    customer = None
    mobile = request.POST.get("customer_mobile", "").strip()
    if mobile:
        try:
            mobile_validator(mobile)
            customer, _ = Customer.objects.get_or_create(mobile=mobile, defaults={"name": request.POST.get("customer_name") or f"Customer {mobile[-4:]}"})
        except Exception:
            messages.error(request, "Invalid customer mobile number - sale recorded as walk-in.")

    coupon_code = request.POST.get("coupon_code", "").strip()
    payment_method = request.POST.get("payment_method", "CASH")
    overall_discount_percent = Decimal(request.POST.get("overall_discount", "0") or 0)

    sale = Sale.objects.create(
        invoice_number=Sale.generate_invoice_number(),
        customer=customer,
        cashier=request.user,
        coupon_code=coupon_code,
        status=Sale.Status.COMPLETED,
    )

    subtotal = Decimal("0")
    gst_total = Decimal("0")
    discount_total = Decimal("0")

    for line in cart:
        variant = get_object_or_404(ProductVariant, pk=line["variant_id"])
        qty = int(line["quantity"])
        if qty < 1:
            continue
        if variant.stock_quantity < qty:
            messages.error(request, f"Not enough stock for {variant}. Available: {variant.stock_quantity}")
            transaction.set_rollback(True)
            return redirect("sales:pos")

        unit_price = Decimal(str(line.get("price", variant.product.effective_price)))
        line_discount = (unit_price * qty) * (overall_discount_percent / Decimal(100))
        gst_percent = variant.product.gst_percent

        item = SaleItem.objects.create(
            sale=sale, variant=variant, quantity=qty, unit_price=unit_price,
            discount_amount=round(line_discount, 2), gst_percent=gst_percent,
        )
        subtotal += unit_price * qty
        discount_total += item.discount_amount
        gst_total += (unit_price * qty - item.discount_amount) * (gst_percent / Decimal(100))

        record_stock_movement(variant, stock_sold=qty, reason="SALE", reference=sale.invoice_number, employee=request.user)

    grand_total = subtotal - discount_total + gst_total
    sale.subtotal = round(subtotal, 2)
    sale.discount_amount = round(discount_total, 2)
    sale.gst_amount = round(gst_total, 2)
    sale.grand_total = round(grand_total, 2)

    # Loyalty points
    shop = ShopSettings.get_solo()
    points = int((grand_total // 100) * shop.loyalty_points_per_100_rupees)
    sale.loyalty_points_earned = points
    sale.save()

    if customer:
        customer.loyalty_points += points
        customer.save(update_fields=["loyalty_points"])

    Payment.objects.create(
        transaction_id=Payment.generate_transaction_id(),
        sale=sale, customer=customer, amount=sale.grand_total,
        method=payment_method, status=Payment.Status.PAID,
        reference_number=request.POST.get("payment_reference", ""),
    )

    messages.success(request, f"Sale {sale.invoice_number} completed successfully.")
    return redirect("sales:invoice", pk=sale.pk)


@login_required
def sale_list(request):
    sales = Sale.objects.select_related("customer", "cashier").all()
    q = request.GET.get("q", "").strip()
    if q:
        sales = sales.filter(
            Q(invoice_number__icontains=q) | Q(customer__name__icontains=q) |
            Q(customer__mobile__icontains=q) | Q(cashier__username__icontains=q)
        )
    return render(request, "sales/sale_list.html", {"sales": sales[:200], "q": q})


@login_required
def invoice(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    shop = ShopSettings.get_solo()
    qr_data_uri = None
    if sale.payments.filter(method="UPI").exists():
        qr_data_uri = _generate_upi_qr(shop, sale)
    return render(request, "sales/invoice.html", {"sale": sale, "shop": shop, "qr_data_uri": qr_data_uri})


def _generate_upi_qr(shop, sale):
    try:
        import qrcode
        import base64
        from io import BytesIO
        upi_uri = f"upi://pay?pa={shop.upi_id}&pn={shop.shop_name.replace(' ', '%20')}&am={sale.grand_total}&cu=INR&tn={sale.invoice_number}"
        img = qrcode.make(upi_uri)
        buf = BytesIO()
        img.save(buf, format="PNG")
        return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()
    except Exception:
        return None


@login_required
def invoice_pdf(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    shop = ShopSettings.get_solo()
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import mm

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'attachment; filename="{sale.invoice_number}.pdf"'
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4
    y = height - 25 * mm

    p.setFont("Helvetica-Bold", 16)
    p.drawString(20 * mm, y, shop.shop_name)
    p.setFont("Helvetica", 9)
    y -= 6 * mm
    p.drawString(20 * mm, y, shop.tagline)
    y -= 5 * mm
    p.drawString(20 * mm, y, shop.address)
    y -= 5 * mm
    p.drawString(20 * mm, y, f"Phone: {shop.phone}  GSTIN: {shop.gstin}")
    y -= 10 * mm

    p.setFont("Helvetica-Bold", 11)
    p.drawString(20 * mm, y, f"Invoice: {sale.invoice_number}")
    p.drawRightString(width - 20 * mm, y, sale.created_at.strftime("%d-%b-%Y %I:%M %p"))
    y -= 6 * mm
    p.setFont("Helvetica", 9)
    p.drawString(20 * mm, y, f"Customer: {sale.customer.name if sale.customer else 'Walk-in Customer'}")
    p.drawRightString(width - 20 * mm, y, f"Cashier: {sale.cashier}")
    y -= 8 * mm

    p.setFont("Helvetica-Bold", 9)
    headers = ["Product", "Size", "Color", "Qty", "Price", "Disc", "GST%", "Amount"]
    xpos = [20, 85, 105, 125, 138, 155, 172, 185]
    for h, x in zip(headers, xpos):
        p.drawString(x * mm, y, h)
    y -= 4 * mm
    p.line(20 * mm, y, width - 20 * mm, y)
    y -= 5 * mm

    p.setFont("Helvetica", 8)
    for item in sale.items.all():
        if y < 30 * mm:
            p.showPage()
            y = height - 25 * mm
        p.drawString(20 * mm, y, item.variant.product.name[:28])
        p.drawString(85 * mm, y, item.variant.size.label)
        p.drawString(105 * mm, y, item.variant.color.name[:10])
        p.drawString(128 * mm, y, str(item.quantity))
        p.drawString(138 * mm, y, f"{item.unit_price}")
        p.drawString(155 * mm, y, f"{item.discount_amount}")
        p.drawString(174 * mm, y, f"{item.gst_percent}%")
        p.drawRightString(width - 20 * mm, y, f"Rs.{item.line_total}")
        y -= 5.5 * mm

    y -= 4 * mm
    p.line(20 * mm, y, width - 20 * mm, y)
    y -= 6 * mm
    p.setFont("Helvetica", 9)
    p.drawRightString(width - 20 * mm, y, f"Subtotal: Rs.{sale.subtotal}")
    y -= 5 * mm
    p.drawRightString(width - 20 * mm, y, f"Discount: Rs.{sale.discount_amount}")
    y -= 5 * mm
    p.drawRightString(width - 20 * mm, y, f"GST: Rs.{sale.gst_amount}")
    y -= 6 * mm
    p.setFont("Helvetica-Bold", 12)
    p.drawRightString(width - 20 * mm, y, f"Grand Total: Rs.{sale.grand_total}")
    y -= 10 * mm
    p.setFont("Helvetica-Oblique", 9)
    p.drawCentredString(width / 2, y, f"Thank you for shopping at {shop.shop_name}")

    p.showPage()
    p.save()
    return response


@login_required
def whatsapp_invoice(request, pk):
    sale = get_object_or_404(Sale, pk=pk)
    shop = ShopSettings.get_solo()
    invoice_url = request.build_absolute_uri(reverse("sales:invoice", args=[sale.pk]))
    text = (
        f"Hello! Thank you for shopping at {shop.shop_name}.\n"
        f"Invoice: {sale.invoice_number}\n"
        f"Amount: ₹{sale.grand_total}\n"
        f"View your invoice: {invoice_url}"
    )
    number = sale.customer.mobile if sale.customer else shop.whatsapp
    from urllib.parse import quote
    wa_link = f"https://wa.me/91{number}?text={quote(text)}"
    return redirect(wa_link)
