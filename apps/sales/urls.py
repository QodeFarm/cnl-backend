from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *

#add your urls

router = DefaultRouter()

router.register(r'sale_order_search', SaleOrderView)
router.register(r'sales_price_list', SalesPriceListView)
router.register(r'sale_order_items', SaleOrderItemsView)
router.register(r'sale_invoice_order_get',SaleInvoiceOrdersView)
# router.register(r'payment_transactions', PaymentTransactionsView)
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
router.register(r'sale_debit_note', SaleDebitNoteViews)
router.register(r'sale_debit_note_item', SaleDebitNoteItemsViews)

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
    # path('sale_order/<uuid:pk>/workflow_pipeline/', ProgressWorkflowView.as_view(), name='workflow-pipeline'),
    path('<str:module_name>/<uuid:object_id>/move_next_stage/', MoveToNextStageGenericView.as_view(), name='move-to-next-stage-generic'),
    path('sale_credit_notes/', SaleCreditNoteViewset.as_view(), name='sale-credit-notes-list-create'),
    path('sale_credit_notes/<str:pk>/', SaleCreditNoteViewset.as_view(), name='sale-credit-notes-detail-update-delete-patch'),
    path('sale_debit_notes/', SaleDebitNoteViewset.as_view(), name='sale-debit-notes-list-create'),
    path('sale_debit_notes/<str:pk>/', SaleDebitNoteViewset.as_view(), name='sale-debit-notes-detail-update-delete-patch'),
    
    path('payment_transactions/', PaymentTransactionAPIView.as_view(),name='payment-transaction-create'),
    path('payment_transactions/<str:customer_id>/', PaymentTransactionAPIView.as_view(), name='customer-payment-transactions-List'),
    path('payment_transactions/transaction/<str:transaction_id>/', PaymentTransactionAPIView.as_view(),name='payment-transaction-Update-API'),
    path('data_for_payment_receipt_table/<str:customer_id>/', FetchSalesInvoicesForPaymentReceiptTable.as_view(), name='sale-Invoice-data-for-payment-receipt-table-by-customer-ID'),
]      