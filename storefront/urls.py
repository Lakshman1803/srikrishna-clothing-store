from django.urls import path
from . import views

app_name = "storefront"

urlpatterns = [
    path("", views.home, name="home"),
    path("category/<slug:slug>/", views.category_page, name="category"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("new-arrivals/", views.new_arrivals, name="new_arrivals"),
    path("offers/", views.offers_page, name="offers"),
    path("search/", views.search, name="search"),
    path("about/", views.about, name="about"),
    path("location/", views.location, name="location"),
    path("contact/", views.contact, name="contact"),
]
