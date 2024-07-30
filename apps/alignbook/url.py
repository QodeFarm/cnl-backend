from django.urls import path
from .views import TrackOrderAndAccountLedger

urlpatterns = [
    path('track_order/', TrackOrderAndAccountLedger.as_view(), name='voucher'),
    path('account_ledger/', TrackOrderAndAccountLedger.as_view(), name='account_ledger'),

]
