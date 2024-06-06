from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, permissions
from .views  import *

router = routers.DefaultRouter()
router.register(r'purchase_orders', PurchaseOrdersViewSet)
router.register(r'purchase_order_items', PurchaseorderItemsViewSet)
router.register(r'purchase_invoice_orders', PurchaseInvoiceOrdersViewSet)
router.register(r'purchase_invoice_items', PurchaseInvoiceItemViewSet)
router.register(r'purchase_return_orders', PurchaseReturnOrdersViewSet) 
router.register(r'purchase_return_items', PurchaseReturnItemsViewSet)
router.register(r'purchase_price_list', PurchasePriceListViewSet)



urlpatterns = [
    path('', include(router.urls)),  
]