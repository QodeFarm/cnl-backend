from django.urls import path
from apps.reports.inventory.views import (
    StockSummaryView,
    StockValuationView,
    ReorderLevelView,
    GodownStockView,
    FastMovingView,
    SlowMovingView,
    StockMovementView,
    StockForecastView,
)

urlpatterns = [
    path("stock-summary/", StockSummaryView.as_view(), name="stock-summary"),
    path("stock-valuation/", StockValuationView.as_view(), name="stock-valuation"),
    path("reorder-level/", ReorderLevelView.as_view(), name="reorder-level"),
    path("godown-stock/", GodownStockView.as_view(), name="godown-stock"),
    path("fast-moving/", FastMovingView.as_view(), name="fast-moving"),
    path("slow-moving/", SlowMovingView.as_view(), name="slow-moving"),
    path("stock-movement/", StockMovementView.as_view(), name="stock-movement"),
    path("stock-forecast/", StockForecastView.as_view(), name="stock-forecast"),
]
