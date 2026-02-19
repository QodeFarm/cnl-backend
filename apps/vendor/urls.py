from django.urls import path, include
from .views import VendorBalanceView, VendorBulkUpdateView, VendorExcelUploadAPIView, VendorExportAPIView, VendorTemplateAPIView, VendorsView, VendorCategoryView, VendorPaymentTermsView, VendorAgentView, VendorAttachmentView, VendorAddressView, VendorViewSet
from rest_framework.routers import DefaultRouter

#add your urls 

router = DefaultRouter()
router.register(r'vendor_get', VendorsView)
router.register(r'vendor_category', VendorCategoryView)
router.register(r'vendor_payment_terms', VendorPaymentTermsView)
router.register(r'vendor_agent', VendorAgentView)
router.register(r'vendor_attachment', VendorAttachmentView)
router.register(r'vendor_address', VendorAddressView)

urlpatterns = [
    path('',include(router.urls)),
    path('bulk-update/', VendorBulkUpdateView.as_view(), name='vendors-bulk-update'),
    path('vendors/', VendorViewSet.as_view(), name='vendor_list_create'),
    path('vendors/bulk-update/', VendorBulkUpdateView.as_view(), name='vendors-bulk-update-alt'),
    path('vendors/<str:pk>/', VendorViewSet.as_view(), name='vendor_detail_update_delete'),
    # === Vendor Balance ===
    path('vendor_balance/', VendorBalanceView.as_view(), name='vendor_balance_list'),
    path('vendor_balance/<uuid:vendor_id>/<str:remaining_payment>/', VendorBalanceView.as_view(), name='vendor_balance_update'),
    path('vendor_balance/<uuid:pk>/', VendorBalanceView.as_view(), name='vendor_balance_detail'),
    
    path('download-template/', VendorTemplateAPIView.as_view(), name='vendor-download-template'),
    path('export-vendors/', VendorExportAPIView.as_view(), name='export_vendors'),
    path('upload-excel/', VendorExcelUploadAPIView.as_view(), name='vendor-upload-excel'),

]
