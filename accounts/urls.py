from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = "accounts"

urlpatterns = [
    path("login/", views.RoleAwareLoginView.as_view(), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("employees/", views.employee_list, name="employee_list"),
    path("employees/add/", views.employee_form, name="employee_add"),
    path("employees/<int:pk>/edit/", views.employee_form, name="employee_edit"),
    path("employees/<int:pk>/toggle/", views.employee_toggle_active, name="employee_toggle"),
    path("audit-log/", views.audit_log, name="audit_log"),
    path("customer-login/", views.customer_login, name="customer_login"),
    path("customer-portal/", views.customer_portal, name="customer_portal"),
    path("customer-logout/", views.customer_logout, name="customer_logout"),
]
