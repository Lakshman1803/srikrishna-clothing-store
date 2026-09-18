from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render, redirect, get_object_or_404

from .models import Expense
from .forms import ExpenseForm


@login_required
def expense_list(request):
    expenses = Expense.objects.all()
    total = expenses.aggregate(t=Sum("amount"))["t"] or 0
    return render(request, "expenses/expense_list.html", {"expenses": expenses[:200], "total": total})


@login_required
def expense_form(request, pk=None):
    instance = get_object_or_404(Expense, pk=pk) if pk else None
    if request.method == "POST":
        form = ExpenseForm(request.POST, instance=instance)
        if form.is_valid():
            exp = form.save(commit=False)
            if not pk:
                exp.employee = request.user
            exp.save()
            messages.success(request, "Expense recorded.")
            return redirect("expenses:expense_list")
    else:
        form = ExpenseForm(instance=instance)
    return render(request, "expenses/expense_form.html", {"form": form, "instance": instance})
