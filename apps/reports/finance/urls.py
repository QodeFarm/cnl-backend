from django.urls import path
from apps.reports.finance.views import (
    GeneralLedgerView,
    TrialBalanceView,
    JournalRegisterView,
    BankBookView,
    CashBookView,
    AccountLedgerView,
    ProfitLossView,
    BalanceSheetView,
    CashFlowView,
    JournalBookView,
    CustomerLedgerView,
    VendorLedgerView,
)

urlpatterns = [
    path("general-ledger/", GeneralLedgerView.as_view(), name="general-ledger"),
    path("trial-balance/", TrialBalanceView.as_view(), name="trial-balance"),
    path("journal-register/", JournalRegisterView.as_view(), name="journal-register"),
    path("bank-book/", BankBookView.as_view(), name="bank-book"),
    path("cash-book/", CashBookView.as_view(), name="cash-book"),
    path("account-ledger/", AccountLedgerView.as_view(), name="account-ledger"),
    path("profit-loss/", ProfitLossView.as_view(), name="profit-loss"),
    path("balance-sheet/", BalanceSheetView.as_view(), name="balance-sheet"),
    path("cash-flow/", CashFlowView.as_view(), name="cash-flow"),
    path("journal-book/", JournalBookView.as_view(), name="journal-book"),
    path("customer-ledger/", CustomerLedgerView.as_view(), name="customer-ledger"),
    path("vendor-ledger/", VendorLedgerView.as_view(), name="vendor-ledger"),
]
