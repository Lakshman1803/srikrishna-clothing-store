from django.urls import path
from . import views

app_name = "inventory"

urlpatterns = [
    path("", views.stock_list, name="stock_list"),
    path("movements/", views.movement_list, name="movement_list"),
    path("adjust/<int:variant_id>/", views.adjust_stock, name="adjust_stock"),
]
