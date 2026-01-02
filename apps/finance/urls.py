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
# router.register(r'expense_categories', ExpenseCategoryViewSet)
# router.register(r'expense_items', ExpenseItemViewSet)
router.register(r'financial_reports', FinancialReportViewSet)
router.register(r'journal_voucher_lines', JournalVoucherLineViewSet)  # For individual line operations

urlpatterns = [
    path('', include(router.urls)),
    path('journal_entries/', JournalEntryView.as_view(), name='journal_entries-list-create'),
    path('journal_entries/<str:pk>/', JournalEntryView.as_view(), name='journal_entries-detail-update-delete'),

    # Custom API View for ExpenseItem (follows same pattern as JournalEntryView)
    path('expense_items/', ExpenseItemView.as_view(), name='expense_items-list-create'),
    path('expense_items/<str:pk>/', ExpenseItemView.as_view(), name='expense_items-detail-update-delete'),

    path('journals/', JournalListCreateAPIView.as_view(), name='journal-list-create'),
    path('journals/<str:journal_id>/', JournalRetrieveUpdateDeleteAPIView.as_view(), name='journal-retrieve-update-delete'),

    path('journal_details/', JournalDetailListCreateAPIView.as_view(), name='journal-detail-list-create'),
    path('journal_details/<str:journal_detail_id>/', JournalDetailRetrieveUpdateDeleteAPIView.as_view(), name='journal-detail-retrieve-update-delete'),

    path('journal_entry_lines_list/<str:input_id>/', JournalEntryLinesAPIView.as_view(),name='JournalEntryLinesAPIView-List-for-customer-or-vendor-ledger-reports'),
    # path('expense_items/', ExpenseItemAPIView.as_view(), name='expenseitem-detail-update-delete'),
    # path('expense_items/<str:pk>/', ExpenseItemAPIView.as_view(), name='expenseitem-detail-update-delete'),
    path('general_accounts/', GeneralAccountsListAPIView.as_view()),
    
    # ======================================
    # JOURNAL VOUCHER URLS
    # ======================================
    # Main Journal Voucher CRUD (with lines and attachments)
    path('journal_vouchers/', JournalVoucherView.as_view(), name='journal_vouchers-list-create'),
    path('journal_vouchers/<str:pk>/', JournalVoucherView.as_view(), name='journal_vouchers-detail-update-delete'),
    
    # Post voucher to ledger
    path('journal_vouchers/<str:pk>/post/', JournalVoucherPostView.as_view(), name='journal_vouchers-post'),
    
    # Pull from expense claim
    path('journal_vouchers/pull_expense_claim/<str:expense_claim_id>/', PullFromExpenseClaimView.as_view(), name='journal_vouchers-pull-expense-claim'),
]