from django.urls import path
from apps.reports.purchase.views import (
    PurchaseRegisterView,
    PendingPurchaseOrdersView,
    PurchaseOrderRegisterView,
    PurchaseReturnRegisterView,
    BillPaymentRegisterView,
    VendorOutstandingView,
    VendorAgingView,
    PurchaseAnalysisProductView,
    PurchaseAnalysisVendorView,
    GstInputSummaryView,
    PurchasePriceVarianceView,
    StockReplenishmentView,
    VendorPerformanceView,
)

urlpatterns = [
    # Purchase Register (13 register_types) — mirrors the Sale Register
    path("register/", PurchaseRegisterView.as_view(), name="purchase-register"),
    path("pending-orders/", PendingPurchaseOrdersView.as_view(), name="pending-purchase-orders"),
    path("order-register/", PurchaseOrderRegisterView.as_view(), name="purchase-order-register"),
    path("return-register/", PurchaseReturnRegisterView.as_view(), name="purchase-return-register"),
    path("bill-payments/", BillPaymentRegisterView.as_view(), name="bill-payment-register"),
    path("vendor-outstanding/", VendorOutstandingView.as_view(), name="vendor-outstanding"),
    path("vendor-aging/", VendorAgingView.as_view(), name="vendor-aging"),
    path("analysis/product/", PurchaseAnalysisProductView.as_view(), name="purchase-analysis-product"),
    path("analysis/vendor/", PurchaseAnalysisVendorView.as_view(), name="purchase-analysis-vendor"),
    path("tax/gst-input-summary/", GstInputSummaryView.as_view(), name="gst-input-summary"),
    path("price-variance/", PurchasePriceVarianceView.as_view(), name="purchase-price-variance"),
    path("stock-replenishment/", StockReplenishmentView.as_view(), name="stock-replenishment"),
    path("vendor-performance/", VendorPerformanceView.as_view(), name="vendor-performance"),
]
