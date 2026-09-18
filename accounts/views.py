import random

from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect, get_object_or_404

from .models import User, AuditLog, log_action
from .forms import EmployeeForm
from customers.models import Customer


class RoleAwareLoginView(LoginView):
    template_name = "accounts/login.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        log_action(self.request.user, "Logged in", request=self.request)
        return response


def is_manager_or_above(user):
    return user.is_authenticated and (user.is_superuser or user.role in
                                       (User.Role.SUPER_ADMIN, User.Role.SHOP_OWNER, User.Role.MANAGER))


@login_required
@user_passes_test(is_manager_or_above)
def employee_list(request):
    employees = User.objects.all().order_by("-created_at")
    return render(request, "accounts/employee_list.html", {"employees": employees})


@login_required
@user_passes_test(is_manager_or_above)
def employee_form(request, pk=None):
    instance = get_object_or_404(User, pk=pk) if pk else None
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=instance)
        if form.is_valid():
            emp = form.save()
            log_action(request.user, f"{'Updated' if pk else 'Created'} employee", emp, request)
            messages.success(request, f"Employee '{emp.username}' saved successfully.")
            return redirect("accounts:employee_list")
    else:
        form = EmployeeForm(instance=instance)
    return render(request, "accounts/employee_form.html", {"form": form, "instance": instance})


@login_required
@user_passes_test(is_manager_or_above)
def employee_toggle_active(request, pk):
    emp = get_object_or_404(User, pk=pk)
    emp.is_active_employee = not emp.is_active_employee
    emp.is_active = emp.is_active_employee
    emp.save()
    log_action(request.user, "Toggled employee active status", emp, request)
    messages.success(request, f"{emp.username} is now {'active' if emp.is_active_employee else 'inactive'}.")
    return redirect("accounts:employee_list")


@login_required
@user_passes_test(is_manager_or_above)
def audit_log(request):
    logs = AuditLog.objects.select_related("user").all()[:300]
    return render(request, "accounts/audit_log.html", {"logs": logs})


# ---------------- Customer-facing OTP login (simulated OTP, no SMS gateway configured) ----------------

def customer_login(request):
    if request.method == "POST":
        step = request.POST.get("step")
        if step == "request_otp":
            mobile = request.POST.get("mobile", "").strip()
            if len(mobile) != 10 or not mobile.isdigit():
                messages.error(request, "Enter a valid 10-digit mobile number.")
                return render(request, "accounts/customer_login.html", {"step": "mobile"})
            otp = f"{random.randint(1000, 9999)}"
            request.session["otp_mobile"] = mobile
            request.session["otp_code"] = otp
            messages.info(request, f"Demo mode: your OTP is {otp} (no SMS gateway configured).")
            return render(request, "accounts/customer_login.html", {"step": "otp", "mobile": mobile})
        elif step == "verify_otp":
            mobile = request.session.get("otp_mobile")
            code = request.session.get("otp_code")
            entered = request.POST.get("otp", "")
            if entered == code and mobile:
                customer, _ = Customer.objects.get_or_create(
                    mobile=mobile, defaults={"name": f"Customer {mobile[-4:]}"}
                )
                request.session["customer_id"] = customer.id
                del request.session["otp_code"]
                messages.success(request, f"Welcome, {customer.name}!")
                return redirect("accounts:customer_portal")
            messages.error(request, "Incorrect OTP. Please try again.")
            return render(request, "accounts/customer_login.html", {"step": "otp", "mobile": mobile})
    return render(request, "accounts/customer_login.html", {"step": "mobile"})


def customer_portal(request):
    customer_id = request.session.get("customer_id")
    if not customer_id:
        return redirect("accounts:customer_login")
    customer = get_object_or_404(Customer, pk=customer_id)
    sales = customer.sales.all().order_by("-created_at")[:50]
    return render(request, "accounts/customer_portal.html", {"customer": customer, "sales": sales})


def customer_logout(request):
    request.session.pop("customer_id", None)
    return redirect("storefront:home")
