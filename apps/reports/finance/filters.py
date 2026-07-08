"""
Finance report filters.

Accounting is posted to LedgerAccounts via JournalEntryLines (debit/credit),
grouped under JournalEntry (voucher). Per-line dates are sparse, so the ledger
line filter uses the parent journal entry's date.
"""

from apps.reports.base.filters import BaseReportFilter


class LedgerLineFilter(BaseReportFilter):
    """Journal entry lines — used by General Ledger and Trial Balance."""
    date_field = "journal_entry_id__entry_date"
    customer_id_field = "customer_id"
    customer_name_field = "customer_id__name"
    vendor_id_field = "vendor_id"
    vendor_name_field = "vendor_id__name"
    default_sort_field = "created_at"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "created_at", "debit", "credit", "voucher_no", "ledger_account_id__name",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        ledger_account_id = params.get("ledger_account_id", "").strip()
        if ledger_account_id:
            queryset = queryset.filter(ledger_account_id=ledger_account_id)
            self._applied["ledger_account_id"] = ledger_account_id

        search_q = self.get_search_query(
            ["voucher_no", "ledger_account_id__name", "description"]
        )
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class JournalEntryFilter(BaseReportFilter):
    """Journal entries (vouchers) — used by the Journal Register / Day Book."""
    date_field = "entry_date"
    default_sort_field = "entry_date"
    default_sort_order = "desc"
    allowed_sort_fields = ["entry_date", "voucher_no", "voucher_type"]

    def apply_secondary_filters(self, queryset):
        params = self.params

        voucher_type = params.get("voucher_type", "").strip()
        if voucher_type:
            queryset = queryset.filter(voucher_type=voucher_type)
            self._applied["voucher_type"] = voucher_type

        search_q = self.get_search_query(["voucher_no", "reference", "description"])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class JournalVoucherLineFilter(BaseReportFilter):
    """Manual journal voucher LINES — used by the Journal Book report.
    Date is the parent voucher's date (lines have no own date)."""
    date_field = "journal_voucher_id__voucher_date"
    default_sort_field = "journal_voucher_id__voucher_date"
    default_sort_order = "desc"
    allowed_sort_fields = ["journal_voucher_id__voucher_date", "amount"]

    def apply_secondary_filters(self, queryset):
        params = self.params

        voucher_type = params.get("voucher_type", "").strip()
        if voucher_type:
            queryset = queryset.filter(journal_voucher_id__voucher_type=voucher_type)
            self._applied["voucher_type"] = voucher_type

        search_q = self.get_search_query([
            "journal_voucher_id__voucher_no",
            "ledger_account_id__name",
            "journal_voucher_id__narration",
            "remark",
        ])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset
