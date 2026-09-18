from django.urls import path
from . import views

app_name = "sales"

urlpatterns = [
    path("", views.pos, name="pos"),
    path("search-product/", views.search_product, name="search_product"),
    path("checkout/", views.checkout, name="checkout"),
    path("list/", views.sale_list, name="sale_list"),
    path("<int:pk>/invoice/", views.invoice, name="invoice"),
    path("<int:pk>/invoice/pdf/", views.invoice_pdf, name="invoice_pdf"),
    path("<int:pk>/whatsapp/", views.whatsapp_invoice, name="whatsapp_invoice"),
]
