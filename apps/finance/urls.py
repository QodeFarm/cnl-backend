#add your urls 
# from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'bank_accounts', BankAccountViewSet)
router.register(r'chart_of_accounts', ChartOfAccountsViewSet)
router.register(r'journal_entries_search', JournalEntryViewSet)
router.register(r'journal_entry_lines', JournalEntryLinesViewSet)
router.register(r'payment_transactions', PaymentTransactionViewSet)
router.register(r'tax_configurations', TaxConfigurationViewSet)
router.register(r'budgets', BudgetViewSet)
router.register(r'expense_claims', ExpenseClaimViewSet)
router.register(r'financial_reports', FinancialReportViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('journal_entries/', JournalEntryView.as_view(), name='journal_entries-list-create'),
    path('journal_entries/<str:pk>/', JournalEntryView.as_view(), name='journal_entries-detail-update-delete'),

    path('journals/', JournalListCreateAPIView.as_view(), name='journal-list-create'),
    path('journals/<str:journal_id>/', JournalRetrieveUpdateDeleteAPIView.as_view(), name='journal-retrieve-update-delete'),

    path('journal_details/', JournalDetailListCreateAPIView.as_view(), name='journal-detail-list-create'),
    path('journal_details/<str:journal_detail_id>/', JournalDetailRetrieveUpdateDeleteAPIView.as_view(), name='journal-detail-retrieve-update-delete'),

    path('journal_entry_lines_list/', JournalEntryLinesAPIView.as_view(),name='JournalEntryLinesAPIView-List-for-customer-or-vendor-ledger-reports')
]
