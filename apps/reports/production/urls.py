from django.urls import path
from apps.reports.production.views import (
    MaterialIssueRegisterView,
    MaterialReceivedRegisterView,
    RawMaterialConsumptionView,
    WorkOrderStatusView,
    ProductionSummaryView,
    BOMReportView,
)

urlpatterns = [
    path("material-issue/", MaterialIssueRegisterView.as_view(), name="material-issue-register"),
    path("material-received/", MaterialReceivedRegisterView.as_view(), name="material-received-register"),
    path("raw-material-consumption/", RawMaterialConsumptionView.as_view(), name="raw-material-consumption"),
    path("work-order-status/", WorkOrderStatusView.as_view(), name="work-order-status"),
    path("production-summary/", ProductionSummaryView.as_view(), name="production-summary"),
    path("bom/", BOMReportView.as_view(), name="bom-report"),
]
