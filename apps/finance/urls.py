#add your urls 
# from django.contrib import admin
from django.urls import path, include
from rest_framework import routers
from .views import *

router = routers.DefaultRouter()
router.register(r'bank_accounts', BankAccountViewSet)
router.register(r'chart_of_accounts', ChartOfAccountsViewSet)
router.register(r'journal_entries_get', JournalEntryViewSet)
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
    path('invoices/', InvoiceListView.as_view(), name='invoice-list'), # test
]
