from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from accounts.models import log_action
from .models import Supplier
from .forms import SupplierForm


@login_required
def supplier_list(request):
    suppliers = Supplier.objects.all()
    return render(request, "suppliers/supplier_list.html", {"suppliers": suppliers})


@login_required
def supplier_form(request, pk=None):
    instance = get_object_or_404(Supplier, pk=pk) if pk else None
    if request.method == "POST":
        form = SupplierForm(request.POST, instance=instance)
        if form.is_valid():
            s = form.save()
            log_action(request.user, f"{'Updated' if pk else 'Created'} supplier", s, request)
            messages.success(request, f"Supplier '{s.name}' saved.")
            return redirect("suppliers:supplier_list")
    else:
        form = SupplierForm(instance=instance)
    return render(request, "suppliers/supplier_form.html", {"form": form, "instance": instance})


@login_required
def supplier_detail(request, pk):
    supplier = get_object_or_404(Supplier, pk=pk)
    purchases = supplier.purchases.all().order_by("-date")
    return render(request, "suppliers/supplier_detail.html", {"supplier": supplier, "purchases": purchases})
