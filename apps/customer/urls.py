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
    path('outstanding/<str:customer_id>/', CustomerOutstandingAPIView.as_view(), name='customer-outstanding'),
    # NEW: Customer Portal Management URLs (Admin)
    path('generate-credentials/<uuid:customer_id>/', 
         GenerateCustomerCredentialsView.as_view(), 
         name='generate-customer-credentials'),
    path('send-credentials/<uuid:customer_id>/', 
         SendCredentialsView.as_view(), 
         name='send-customer-credentials'),
    
    # ========== CUSTOMER FORGOT PASSWORD URLs (Public - No auth required) ==========
    # Step 1: Request password reset email
    path('portal/validate-token/', 
         ValidateResetTokenView.as_view(), 
         name='validate-reset-token'),
    
    path('portal/forgot-password/', 
         SendCustomerPasswordResetEmailView.as_view(), 
         name='customer-forgot-password'),
    
    # Step 2: Reset password using token from email
    path('portal/reset-password/<str:token>/', 
         CustomerPasswordResetView.as_view(), 
         name='customer-reset-password'),
    
    # NEW: Customer Portal Public URLs (No authentication required)
    path('portal/login/', 
         CustomerPortalLoginView.as_view(), 
         name='customer-portal-login'),
    path('portal/logout/', 
         CustomerPortalLogoutView.as_view(), 
         name='customer-portal-logout'),
    path('portal/check-auth/', 
         CheckCustomerAuthView.as_view(), 
         name='customer-check-auth'),
    
    # NEW: Customer Portal Protected URLs (Requires authentication)
    path('portal/profile/', CustomerProfileView.as_view(), name='customer-portal-profile'),
    
]
