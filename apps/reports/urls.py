from django.urls import path, include

urlpatterns = [
    path("sales/", include("apps.reports.sales.urls")),
    path("purchase/", include("apps.reports.purchase.urls")),
    path("inventory/", include("apps.reports.inventory.urls")),
    path("production/", include("apps.reports.production.urls")),
    path("finance/", include("apps.reports.finance.urls")),
    path("gst/", include("apps.reports.gst.urls")),
]
