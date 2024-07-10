from django.contrib import admin
from django.urls import path, include
from rest_framework import routers, permissions
from .views  import *

router = routers.DefaultRouter()
router.register(r'purchase_orders_get', PurchaseOrdersViewSet)
router.register(r'purchase_order_items', PurchaseorderItemsViewSet)
router.register(r'purchase_invoice_orders_get', PurchaseInvoiceOrdersViewSet)
router.register(r'purchase_invoice_items', PurchaseInvoiceItemViewSet)
router.register(r'purchase_return_orders_get', PurchaseReturnOrdersViewSet) 
router.register(r'purchase_return_items', PurchaseReturnItemsViewSet)
router.register(r'purchase_price_list', PurchasePriceListViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('purchase_order/', PurchaseOrderViewSet.as_view(), name='purchase-order-list-create'),
    path('purchase_order/<str:pk>/', PurchaseOrderViewSet.as_view(), name='purchase-order-detail-update-delete'),
    path('purchase_invoice_order/', PurchaseInvoiceOrderViewSet.as_view(), name='purchase-invoice-order-list-create'),
    path('purchase_invoice_order/<str:pk>/', PurchaseInvoiceOrderViewSet.as_view(), name='purchase-invoice-order-detail-update-delete'),
    path('purchase_return_order/', PurchaseReturnOrderViewSet.as_view(), name='purchase-return-order-list-create'),
    path('purchase_return_order/<str:pk>/', PurchaseReturnOrderViewSet.as_view(), name='purchase-return-order-detail-update-delete'),
]