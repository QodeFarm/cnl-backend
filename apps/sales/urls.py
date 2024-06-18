from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

#add your urls

router = DefaultRouter()

router.register(r'sale_order', SaleOrderView)
router.register(r'sales_price_list', SalesPriceListView)
router.register(r'sale_order_items', SaleOrderItemsView)
router.register(r'sale_invoice_order',SaleInvoiceOrdersView)
router.register(r'payment_transactions', PaymentTransactionsView)
router.register(r'sale_invoice_items', SaleInvoiceItemsView)
router.register(r'sale_return_orders', SaleReturnOrdersView)
router.register(r'sale_return_items', SaleReturnItemsView)
router.register(r'order_attachements', OrderAttachmentsView)
router.register(r'order_shipments', OrderShipmentsView)

urlpatterns = [
    path('',include(router.urls)),
    path('sales-order-operation/', SaleOrderCreateView.as_view(), name='sales-order-operation'),
]



