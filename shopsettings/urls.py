from django.urls import path
from . import views

app_name = "shopsettings"

urlpatterns = [
    path("", views.edit_settings, name="edit"),
    path("backup/", views.backup, name="backup"),
]
