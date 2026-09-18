from django.urls import path
from . import views

app_name = "expenses"

urlpatterns = [
    path("", views.expense_list, name="expense_list"),
    path("add/", views.expense_form, name="expense_add"),
    path("<int:pk>/edit/", views.expense_form, name="expense_edit"),
]
