from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path("admin/", admin.site.urls),
    path("accounts/", include("accounts.urls")),
    path("dashboard/", include("dashboard.urls")),
    path("pos/", include("sales.urls")),
    path("inventory/", include("inventory.urls")),
    path("customers/", include("customers.urls")),
    path("suppliers/", include("suppliers.urls")),
    path("purchases/", include("purchases.urls")),
    path("expenses/", include("expenses.urls")),
    path("returns/", include("returns_exchanges.urls")),
    path("offers/", include("offers.urls")),
    path("reports/", include("dashboard.report_urls")),
    path("settings/", include("shopsettings.urls")),
    path("", include("storefront.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
