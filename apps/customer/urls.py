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
    path('customers/', CustomerCreateViews.as_view(), name='customers-create'),
    path('customers/<str:pk>/', CustomerCreateViews.as_view(), name='customers-details'),
    path('customers_balance/', CustomerBalanceView.as_view(), name='get-all-customers-balance'),
    path('customers_balance/<str:pk>/', CustomerBalanceView.as_view(), name='get-customer-balance'),
]
