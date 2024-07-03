from django.urls import path, include
from .views import VendorsView, VendorCategoryView, VendorPaymentTermsView, VendorAgentView, VendorAttachmentView, VendorAddressView, VendorViewSet
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
    path('vendor/', VendorViewSet.as_view(), name='vendor-list-create'),
    path('vendor/<str:pk>/', VendorViewSet.as_view(), name='vendor-detail-update-delete'),
]
