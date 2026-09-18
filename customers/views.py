from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404

from .models import Customer


@login_required
def customer_list(request):
    customers = Customer.objects.all()
    q = request.GET.get("q", "").strip()
    if q:
        customers = customers.filter(Q(name__icontains=q) | Q(mobile__icontains=q) | Q(email__icontains=q))
    return render(request, "customers/customer_list.html", {"customers": customers[:300], "q": q})


@login_required
def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    sales = customer.sales.all().order_by("-created_at")
    returns = []
    for s in sales:
        returns.extend(s.returns.all())
    return render(request, "customers/customer_detail.html", {"customer": customer, "sales": sales, "returns": returns})
