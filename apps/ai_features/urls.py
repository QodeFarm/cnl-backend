from django.urls import path
from apps.ai_features.views import (
    LowStockAlertView, StockForecastAlertView, DebtDefaulterView,
    InactiveCustomerView, DeadStockView, BestVendorView,
    WorkOrderSuggestionView, AutoPurchaseOrderView,
    DemandForecastView, ChurnRiskView, CashFlowForecastView,
    ExpenseAnomalyView, PriceVarianceView, RawMaterialForecastView,
    ProfitMarginView, MoneyBleedingView, SeasonalityHeatmapView,
    WhatIfSimulatorView,
)

urlpatterns = [
    path('low-stock/', LowStockAlertView.as_view(), name='low-stock-alerts'),
    path('stock-forecast/', StockForecastAlertView.as_view(), name='stock-forecast-alerts'),
    path('debt-defaulters/', DebtDefaulterView.as_view(), name='debt-defaulter-alerts'),
    path('inactive-customers/', InactiveCustomerView.as_view(), name='inactive-customer-alerts'),
    path('dead-stock/', DeadStockView.as_view(), name='dead-stock-alerts'),
    path('best-vendor/', BestVendorView.as_view(), name='best-vendor-analysis'),
    path('work-order-suggestions/', WorkOrderSuggestionView.as_view(), name='work-order-suggestions'),
    path('auto-purchase-order/', AutoPurchaseOrderView.as_view(), name='auto-purchase-order'),
    path('demand-forecast/', DemandForecastView.as_view(), name='demand-forecast'),
    path('churn-risk/', ChurnRiskView.as_view(), name='churn-risk'),
    path('cash-flow-forecast/', CashFlowForecastView.as_view(), name='cash-flow-forecast'),
    path('expense-anomaly/', ExpenseAnomalyView.as_view(), name='expense-anomaly'),
    path('price-variance/', PriceVarianceView.as_view(), name='price-variance'),
    path('raw-material-forecast/', RawMaterialForecastView.as_view(), name='raw-material-forecast'),
    path('profit-margin/', ProfitMarginView.as_view(), name='profit-margin'),
    path('money-bleeding/', MoneyBleedingView.as_view(), name='money-bleeding'),
    path('seasonality-heatmap/', SeasonalityHeatmapView.as_view(), name='seasonality-heatmap'),
    path('what-if-simulator/', WhatIfSimulatorView.as_view(), name='what-if-simulator'),
]
