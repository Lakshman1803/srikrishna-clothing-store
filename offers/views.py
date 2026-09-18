from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404

from .models import Offer
from .forms import OfferForm


@login_required
def offer_list(request):
    offers = Offer.objects.all()
    return render(request, "offers/offer_list.html", {"offers": offers})


@login_required
def offer_form(request, pk=None):
    instance = get_object_or_404(Offer, pk=pk) if pk else None
    if request.method == "POST":
        form = OfferForm(request.POST, instance=instance)
        if form.is_valid():
            form.save()
            messages.success(request, "Offer saved.")
            return redirect("offers:offer_list")
    else:
        form = OfferForm(instance=instance)
    return render(request, "offers/offer_form.html", {"form": form, "instance": instance})
