from django.urls import path
from . import views

urlpatterns = [
    path("export/<str:report_type>/", views.export_report, name="export_report"),
]
