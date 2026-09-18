from django.urls import path
from . import views

app_name = "offers"

urlpatterns = [
    path("", views.offer_list, name="offer_list"),
    path("add/", views.offer_form, name="offer_add"),
    path("<int:pk>/edit/", views.offer_form, name="offer_edit"),
]
