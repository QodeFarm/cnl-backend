from django.urls import path
from apps.reports.sales.views import (
    SalesRegisterView,
    PendingSaleOrdersView,
    PendingChallansView,
    SaleOrderRegisterView,
    SaleChallanRegisterView,
    SaleReturnRegisterView,
    CreditDebitNoteRegisterView,
    PaymentReminderView,
    CustomerAgingView,
    NewCustomersView,
    NoSalesCustomersView,
    LimitExceededCustomersView,
    SalesOrderAnalysisView,
    ProductSalesAnalysisView,
    CustomerSalesAnalysisView,
    SalespersonAnalysisView,
    ProfitMarginView,
    SalesTrendView,
    GstSummaryView,
)

urlpatterns = [
    # Step 2 — Sale Register (13 register_types)
    path("register/", SalesRegisterView.as_view(), name="sales-register"),

    # Step 3 — Pending Registers
    path("pending-orders/", PendingSaleOrdersView.as_view(), name="pending-sale-orders"),
    path("pending-challans/", PendingChallansView.as_view(), name="pending-challans"),

    # Step 3 — Trading Registers
    path("order-register/", SaleOrderRegisterView.as_view(), name="sale-order-register"),
    path("challan-register/", SaleChallanRegisterView.as_view(), name="sale-challan-register"),
    path("return-register/", SaleReturnRegisterView.as_view(), name="sale-return-register"),
    path("credit-debit-notes/", CreditDebitNoteRegisterView.as_view(), name="credit-debit-notes"),

    # Step 4 — Payment & Outstanding
    path("payment-reminder/", PaymentReminderView.as_view(), name="payment-reminder"),
    path("customer-aging/", CustomerAgingView.as_view(), name="customer-aging"),

    # Step 5 — MIS Reports + Sales Order Analysis
    path("mis/new-customers/", NewCustomersView.as_view(), name="mis-new-customers"),
    path("mis/no-sales-customers/", NoSalesCustomersView.as_view(), name="mis-no-sales-customers"),
    path("mis/limit-exceeded/", LimitExceededCustomersView.as_view(), name="mis-limit-exceeded"),
    path("order-analysis/", SalesOrderAnalysisView.as_view(), name="sales-order-analysis"),

    # Step 6 — Analysis Reports
    path("analysis/product/", ProductSalesAnalysisView.as_view(), name="analysis-product"),
    path("analysis/customer/", CustomerSalesAnalysisView.as_view(), name="analysis-customer"),
    path("analysis/salesperson/", SalespersonAnalysisView.as_view(), name="analysis-salesperson"),
    path("profit-margin/", ProfitMarginView.as_view(), name="profit-margin"),
    path("sales-trend/", SalesTrendView.as_view(), name="sales-trend"),
    path("tax/gst-summary/", GstSummaryView.as_view(), name="gst-summary"),
]
