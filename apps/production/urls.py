from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'bill_of_materials', BillOfMaterialsViewSet)
router.register(r'production_statuses', ProductionStatusViewSet)
router.register(r'work_orders_get', WorkOrderViewSet)
router.register(r'machines', MachineViewSet)
router.register(r'production_workers', ProductionWorkerViewSet)
router.register(r'work_order_stages', WorkOrderStageViewSet)
router.register(r'raw_materials', RawMaterialViewSet)
router.register(r'default_machinery', DefaultMachineryViewSet)
router.register(r'work_order_machine', WorkOrderMachineViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('work_order/', WorkOrderAPIView.as_view(), name='work-order-list-create'),
    path('work_order/<str:pk>/', WorkOrderAPIView.as_view(), name='work-order-detail-update-delete'),    
]