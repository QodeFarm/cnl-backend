from django.urls import path, include
from .views import *
from rest_framework.routers import DefaultRouter

#add your urls

router = DefaultRouter()

router.register(r'sale_order_search', SaleOrderView)
router.register(r'sales_price_list', SalesPriceListView)
router.register(r'sale_order_items', SaleOrderItemsView)
router.register(r'sale_invoice_order_get',SaleInvoiceOrdersView)
router.register(r'payment_transactions', PaymentTransactionsView)
router.register(r'sale_invoice_items', SaleInvoiceItemsView)
router.register(r'sale_return_orders_get', SaleReturnOrdersView)
router.register(r'sale_return_items', SaleReturnItemsView)
router.register(r'order_attachements', OrderAttachmentsView)
router.register(r'order_shipments', OrderShipmentsView)
router.register(r'quick_packs_get', QuickPacksView)
router.register(r'quick_pack_items_get', QuickPacksItemsView)
router.register(r'workflows', WorkflowViewSet)
router.register(r'workflow_stages', WorkflowStageViewSet)
router.register(r'sale_receipts', SaleReceiptViewSet)
router.register(r'sale_credit_note', SaleCreditNoteViews)
router.register(r'sale_credit_note_item', SaleCreditNoteItemsViews)

urlpatterns = [
    path('',include(router.urls)),
    path('sale_order/', SaleOrderViewSet.as_view(), name='sales-order-list-create'),
    path('sale_order/<str:pk>/', SaleOrderViewSet.as_view(), name='sales-order-detail-update-delete'),
    path('sale_invoice_order/', SaleInvoiceOrdersViewSet.as_view(), name='sales-invoice-orders-list-create'),
    path('sale_invoice_order/<str:pk>/', SaleInvoiceOrdersViewSet.as_view(), name='sales-invoice-orders-detail-update-delete'),
    path('sale_return_order/', SaleReturnOrdersViewSet.as_view(), name='sales-return-orders-list-create'),
    path('sale_return_order/<str:pk>/', SaleReturnOrdersViewSet.as_view(), name='sales-return-orders-detail-update-delete'),
    path('quick_pack/', QuickPackCreateViewSet.as_view(), name='quickpack-list-create'),
    path('quick_pack/<str:pk>/', QuickPackCreateViewSet.as_view(), name='quickpack-detail-update-delete'),
    path('sale_reciept/', SaleReceiptCreateViewSet.as_view(), name='salereciept-list-create'),
    path('sale_reciept/<str:pk>/', SaleReceiptCreateViewSet.as_view(), name='salereciept-detail-update-delete'),
    path('work_flow/', WorkflowCreateViewSet.as_view(), name='Workflow-list-create'),
    path('work_flow/<str:pk>/', WorkflowCreateViewSet.as_view(), name='Workflow-detail-update-delete'),
    path('sale_order/<uuid:pk>/workflow_pipeline/', ProgressWorkflowView.as_view(), name='workflow-pipeline'),
    path('sale_credit_notes/', SaleCreditNoteViewset.as_view(), name='sale-credit-notes-list-create'),
    path('sale_credit_notes/<str:pk>/', SaleCreditNoteViewset.as_view(), name='sale-credit-notes-detail-update-delete')

]