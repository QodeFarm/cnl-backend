from .views import *
from rest_framework import routers
from django.urls import path, include


router = routers.DefaultRouter()
router.register(r'customer', CustomerViews)
router.register(r'ledger_accounts', LedgerAccountsViews)
router.register(r'customers_addresses', CustomerAddressesViews)
router.register(r'customers_attachments', CustomerAttachmentsViews)

urlpatterns = [
    path('', include(router.urls)),
    path('bulk-update/', CustomerBulkUpdateView.as_view(), name='customers-bulk-update'),
    path('customers/', CustomerCreateViews.as_view(), name='customers-create'),
    path('customers/bulk-update/', CustomerBulkUpdateView.as_view(), name='customers-bulk-update-alt'),
    path('customers/<str:pk>/', CustomerCreateViews.as_view(), name='customers-details'),
    path('customers_balance/', CustomerBalanceView.as_view(), name='get-all-customers-balance'),
    path('customers_balance/<str:pk>/', CustomerBalanceView.as_view(), name='get-customer-balance'),
    path('download-template/', CustomerTemplateAPIView.as_view(), name='download_customer_template'),
    path('export-customers/', CustomerExportAPIView.as_view(), name='export_customers'),
    path('upload-excel/', CustomerExcelUploadAPIView.as_view(), name='upload_excel'),
]
