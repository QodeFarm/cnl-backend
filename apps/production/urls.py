from django.urls import path, include
from rest_framework import routers
from .views import BillOfMaterialsViewSet, ProductionStatusViewSet, WorkOrderViewSet, InventoryViewSet, MachineViewSet, LaborViewSet

router = routers.DefaultRouter()
router.register(r'bill_of_materials', BillOfMaterialsViewSet)
router.register(r'production_statuses', ProductionStatusViewSet)
router.register(r'work_orders', WorkOrderViewSet)
router.register(r'inventory', InventoryViewSet)
router.register(r'machines', MachineViewSet)
router.register(r'labor', LaborViewSet)

urlpatterns = [
    path('', include(router.urls)),
]