from django.contrib import messages
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect

from catalog.models import Category, Product
from offers.models import Offer
from shopsettings.models import ShopSettings


def home(request):
    shop = ShopSettings.get_solo()
    categories = Category.objects.all()
    new_arrivals = Product.objects.filter(is_active=True, is_new_arrival=True)[:8]
    best_sellers = Product.objects.filter(is_active=True, is_best_seller=True)[:8]
    offers = Offer.objects.filter(is_active=True)
    running_offers = [o for o in offers if o.is_currently_running][:3]
    category_products = [(c, Product.objects.filter(is_active=True, category=c)[:4]) for c in categories]
    return render(request, "storefront/home.html", {
        "shop": shop, "categories": categories, "new_arrivals": new_arrivals,
        "best_sellers": best_sellers, "running_offers": running_offers, "category_sections": category_products,
    })


def category_page(request, slug):
    category = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(is_active=True, category=category)
    subcategory_slug = request.GET.get("sub")
    if subcategory_slug:
        products = products.filter(subcategory__slug=subcategory_slug)
    return render(request, "storefront/category.html", {"category": category, "products": products})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    variants = product.variants.select_related("size", "color").all()
    sizes = sorted({v.size for v in variants}, key=lambda s: s.display_order)
    colors = sorted({v.color for v in variants}, key=lambda c: c.name)
    related = Product.objects.filter(category=product.category, is_active=True).exclude(pk=product.pk)[:4]
    return render(request, "storefront/product_detail.html", {
        "product": product, "sizes": sizes, "colors": colors, "related": related,
    })


def new_arrivals(request):
    products = Product.objects.filter(is_active=True, is_new_arrival=True)
    return render(request, "storefront/product_grid.html", {"products": products, "title": "New Arrivals"})


def offers_page(request):
    offers = [o for o in Offer.objects.filter(is_active=True) if o.is_currently_running]
    return render(request, "storefront/offers.html", {"offers": offers})


def search(request):
    q = request.GET.get("q", "").strip()
    products = Product.objects.filter(is_active=True)
    if q:
        products = products.filter(Q(name__icontains=q) | Q(sku__icontains=q) | Q(description__icontains=q))
    return render(request, "storefront/product_grid.html", {"products": products, "title": f"Search results for '{q}'", "q": q})


def about(request):
    return render(request, "storefront/about.html")


def location(request):
    shop = ShopSettings.get_solo()
    return render(request, "storefront/location.html", {"shop": shop})


def contact(request):
    shop = ShopSettings.get_solo()
    if request.method == "POST":
        messages.success(request, "Thank you! Your message has been noted. We'll get back to you soon.")
        return redirect("storefront:contact")
    return render(request, "storefront/contact.html", {"shop": shop})
