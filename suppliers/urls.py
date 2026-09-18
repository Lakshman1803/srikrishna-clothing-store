from django.urls import path
from . import views

app_name = "suppliers"

urlpatterns = [
    path("", views.supplier_list, name="supplier_list"),
    path("add/", views.supplier_form, name="supplier_add"),
    path("<int:pk>/edit/", views.supplier_form, name="supplier_edit"),
    path("<int:pk>/", views.supplier_detail, name="supplier_detail"),
]
