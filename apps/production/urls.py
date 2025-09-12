from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'bom_search', BOMViewSet)
router.register(r'bill_of_materials', BillOfMaterialsViewSet)
router.register(r'production_statuses', ProductionStatusViewSet)
router.register(r'work_orders_get', WorkOrderViewSet)
router.register(r'completed_quantities', CompletedQuantityViewSet)
router.register(r'machines', MachineViewSet)
router.register(r'production_workers', ProductionWorkerViewSet)
router.register(r'work_order_stages', WorkOrderStageViewSet)
router.register(r'raw_materials', RawMaterialViewSet)
router.register(r'default_machinery', DefaultMachineryViewSet)
router.register(r'work_order_machine', WorkOrderMachineViewSet)
router.register(r'stock_journal', StockJournalViewSet)
# router.register(r'stock_summary', StockSummaryViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('bom/', BOMView.as_view(), name='bill-of-material-list-create'),
    path('bom/<str:pk>/', BOMView.as_view(), name='bill-of-material-detail-update-delete'),      
    path('work_order/', WorkOrderAPIView.as_view(), name='work-order-list-create'),
    path('work_order/<str:pk>/', WorkOrderAPIView.as_view(), name='work-order-detail-update-delete'),   
    path('material-issues/', MaterialIssueView.as_view(), name='material-issue-list-create'),
    path('material-issues/<str:pk>/', MaterialIssueView.as_view(), name='material-issue-detail-update-delete'), 
    path('material-received/', MaterialReceivedView.as_view(), name='material-received-list-create'),
    path('material-received/<str:pk>/', MaterialReceivedView.as_view(), name='material-received-detail-update-delete'),
    path('stock-summary/', StockSummaryAPIView.as_view(), name='stock-summary-api'),
]