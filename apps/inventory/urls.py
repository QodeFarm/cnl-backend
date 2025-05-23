from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, permissions
from .views  import *

router = routers.DefaultRouter()
router.register(r'warehouses', WarehousesViewSet)
router.register(r'warehouse_locations', WarehouseLocationsViewSet)
router.register(r'inventory_block_config', InventoryBlockConfigViewSet)
router.register(r'blocked_inventory', BlockedInventoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]