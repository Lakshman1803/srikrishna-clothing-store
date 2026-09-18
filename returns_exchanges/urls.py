from django.urls import path
from . import views

app_name = "returns_exchanges"

urlpatterns = [
    path("", views.return_list, name="return_list"),
    path("new/", views.return_create, name="return_create"),
    path("find-invoice/", views.find_invoice, name="find_invoice"),
]
