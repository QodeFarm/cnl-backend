"""
Finance reports — double-entry ledger (LedgerAccounts + JournalEntry/Lines).

Field reality (verified against models + cnlprod_2 data):
  JournalEntry (journalentries):     entry_date, voucher_no, voucher_type, reference, description
  JournalEntryLines (journalentrylines): ledger_account_id(->LedgerAccounts), voucher_no,
        debit, credit, customer_id, vendor_id, description, journal_entry_id, is_deleted
  LedgerAccounts: name, code, type ('Bank'|'Cash'|'General'), ledger_group_id
  LedgerGroups:   nature ('Asset'|'Liability'|'Income'|'Expense'|'AccountsReceivable')
  (ChartOfAccounts has 0 rows — accounting is on LedgerAccounts. Account type drives
   Bank/Cash Book; ledger-group nature drives P&L and Balance Sheet.)
"""

from decimal import Decimal

from django.db.models import Count, Sum, Value, DecimalField, Q
from django.db.models.functions import Coalesce

from rest_framework.response import Response

from apps.reports.base.views import BaseReportView
from apps.reports.base.pagination import get_page_and_limit, paginate_list
from apps.reports.base.response import build_report_response
from apps.reports.finance.filters import (
    LedgerLineFilter, JournalEntryFilter, JournalVoucherLineFilter,
)
from apps.finance.models import JournalEntry, JournalEntryLines, JournalVoucherLine

ZERO = Value(Decimal("0.00"), output_field=DecimalField(max_digits=18, decimal_places=2))


class GeneralLedgerView(BaseReportView):
    """Journal Book — every debit/credit line with voucher, account and party."""
    report_type = "general_ledger"
    report_label = "General Ledger (Journal Book)"
    module = "finance"
    filter_class = LedgerLineFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            JournalEntryLines.objects
            .filter(is_deleted=False)
            .select_related("ledger_account_id", "journal_entry_id", "customer_id", "vendor_id")
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_lines=Count("journal_entry_line_id"),
            total_debit=Coalesce(Sum("debit"), ZERO),
            total_credit=Coalesce(Sum("credit"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for ln in queryset:
            je = ln.journal_entry_id
            party = None
            if ln.customer_id:
                party = ln.customer_id.name
            elif ln.vendor_id:
                party = ln.vendor_id.name
            rows.append({
                "journal_entry_line_id": str(ln.journal_entry_line_id),
                # real transaction date if set, else the posting/recording date
                # (created_at) — like the legacy Account Ledger; never blank "—".
                "entry_date": (je.entry_date if je and je.entry_date else ln.entry_date)
                or (ln.created_at.date() if ln.created_at else None),
                "voucher_no": ln.voucher_no,
                "account": ln.ledger_account_id.name if ln.ledger_account_id else None,
                "account_code": ln.ledger_account_id.code if ln.ledger_account_id else None,
                "party": party,
                "debit": ln.debit,
                "credit": ln.credit,
                "description": ln.description,
            })
        return rows


class TrialBalanceView(BaseReportView):
    """Trial Balance — total debit, credit and net balance per ledger account."""
    report_type = "trial_balance"
    report_label = "Trial Balance"
    module = "finance"
    cache_ttl = 600

    @staticmethod
    def _flat_params(request):
        params = dict(request.query_params)
        return {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in params.items()}

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached

        flat = self._flat_params(request)
        page, limit = get_page_and_limit(request)
        db_alias = self._get_db_alias(request) or "default"
        cache_params = {**flat, "_page": page, "_limit": limit}

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        f = LedgerLineFilter(flat)
        base_qs = (
            JournalEntryLines.objects.using(db_alias)
            .filter(is_deleted=False)
            .select_related("ledger_account_id")
        )
        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        summary_agg = base_qs.aggregate(
            total_debit=Coalesce(Sum("debit"), ZERO),
            total_credit=Coalesce(Sum("credit"), ZERO),
        )

        agg = (
            base_qs
            .values("ledger_account_id", "ledger_account_id__name", "ledger_account_id__code")
            .annotate(
                total_debit=Coalesce(Sum("debit"), ZERO),
                total_credit=Coalesce(Sum("credit"), ZERO),
            )
            .order_by("ledger_account_id__name")
        )
        rows = []
        for r in agg:
            debit = r["total_debit"] or Decimal("0.00")
            credit = r["total_credit"] or Decimal("0.00")
            net = debit - credit
            rows.append({
                "account_id": str(r["ledger_account_id"]) if r["ledger_account_id"] else "",
                "account": r["ledger_account_id__name"] or "(Unassigned)",
                "account_code": r["ledger_account_id__code"],
                "total_debit": debit,
                "total_credit": credit,
                "balance": abs(net),
                "balance_type": "Dr" if net >= 0 else "Cr",
            })

        summary = {
            "total_accounts": len(rows),
            "total_debit": str(summary_agg["total_debit"]),
            "total_credit": str(summary_agg["total_credit"]),
        }
        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, resp.data, self.cache_ttl)
        return resp


class JournalRegisterView(BaseReportView):
    """Journal Register / Day Book — all journal vouchers with date and type."""
    report_type = "journal_register"
    report_label = "Journal Register (Day Book)"
    module = "finance"
    filter_class = JournalEntryFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return JournalEntry.objects.filter(is_deleted=False)

    def get_summary(self, queryset):
        return queryset.aggregate(total_vouchers=Count("journal_entry_id"))

    def serialize(self, queryset):
        rows = []
        for je in queryset:
            rows.append({
                "journal_entry_id": str(je.journal_entry_id),
                "voucher_no": je.voucher_no,
                "entry_date": je.entry_date,
                "voucher_type": je.voucher_type,
                "reference": je.reference,
                "description": je.description,
            })
        return rows


class _FinanceCustomView(BaseReportView):
    """Shared helpers for finance views that build rows in Python (running
    balance / nature grouping) rather than a plain serializer."""
    module = "finance"

    @staticmethod
    def _flat_params(request):
        params = dict(request.query_params)
        return {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in params.items()}

    def _ctx(self, request):
        flat = self._flat_params(request)
        page, limit = get_page_and_limit(request)
        db_alias = self._get_db_alias(request) or "default"
        cache_params = {**flat, "_page": page, "_limit": limit}
        return flat, page, limit, db_alias, cache_params


class _LedgerRunningView(_FinanceCustomView):
    """Ledger lines with a per-account running balance (Bank/Cash/Account Ledger)."""
    account_type = None  # None = all accounts, else 'Bank' / 'Cash'
    cache_ttl = 300

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        flat, page, limit, db_alias, cache_params = self._ctx(request)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        f = LedgerLineFilter(flat)
        qs = (
            JournalEntryLines.objects.using(db_alias)
            .filter(is_deleted=False)
            .select_related("ledger_account_id", "journal_entry_id", "customer_id", "vendor_id")
        )
        if self.account_type:
            qs = qs.filter(ledger_account_id__type=self.account_type)
        qs = f.apply(qs)
        filters_applied = f.get_applied_filters()

        # Running balance is computed over the FULL ordered set, then paginated —
        # so page 2 continues from page 1. Two fixes vs the naive version:
        #  (1) key the running total on the unique account ID, NOT the name —
        #      account names are not unique, so two "Cash" accounts must not merge.
        #  (2) order by the TRANSACTION date (journal entry date, else line date)
        #      so the ladder follows the dates shown; created_at is only a stable
        #      tie-breaker. Account name kept first so groups list alphabetically.
        qs = qs.annotate(_sort_date=Coalesce("journal_entry_id__entry_date", "entry_date"))
        lines = list(qs.order_by(
            "ledger_account_id__name", "ledger_account_id_id", "_sort_date", "created_at",
        ))
        rows, running = [], {}
        total_debit = total_credit = Decimal("0.00")
        for ln in lines:
            acc_key = ln.ledger_account_id_id  # unique id (None = unassigned)
            if ln.ledger_account_id:
                la = ln.ledger_account_id
                acc = la.name or la.code or "(No name)"  # don't show blank for unnamed accounts
            else:
                acc = "(Unassigned)"
            party = None
            if ln.customer_id:
                party = ln.customer_id.name
            elif ln.vendor_id:
                party = ln.vendor_id.name
            d = ln.debit or Decimal("0.00")
            c = ln.credit or Decimal("0.00")
            running[acc_key] = running.get(acc_key, Decimal("0.00")) + d - c
            total_debit += d
            total_credit += c
            je = ln.journal_entry_id
            rows.append({
                "journal_entry_line_id": str(ln.journal_entry_line_id),
                "_ak": str(acc_key),  # internal key for per-page account grouping
                # real transaction date if set, else the posting/recording date
                # (created_at) — like the legacy Account Ledger; never blank "—".
                "entry_date": (je.entry_date if je and je.entry_date else ln.entry_date)
                or (ln.created_at.date() if ln.created_at else None),
                "voucher_no": ln.voucher_no,
                "account": acc,
                "party": party,
                "debit": d,
                "credit": c,
                "running_balance": running[acc_key],
                "description": ln.description,
            })

        summary = {
            "total_accounts": len(running),
            "total_lines": len(rows),
            "total_debit": str(total_debit),
            "total_credit": str(total_credit),
        }
        data, total = paginate_list(rows, page, limit)
        # Account shown ONCE per group, blanked on repeats — done on the PAGE (after
        # slicing) so each page's first row keeps its account label across page cuts.
        prev = object()
        for r in data:
            ak = r.pop("_ak", None)
            if ak == prev:
                r["account"] = ""
            prev = ak
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, resp.data, self.cache_ttl)
        return resp


class BankBookView(_LedgerRunningView):
    """Bank Book — all bank-account transactions with running balance."""
    report_type = "bank_book"
    report_label = "Bank Book"
    account_type = "Bank"


class CashBookView(_LedgerRunningView):
    """Cash Book — cash receipts and payments with running balance."""
    report_type = "cash_book"
    report_label = "Cash Book"
    account_type = "Cash"


class AccountLedgerView(_LedgerRunningView):
    """Account Ledger — any account's transactions with running balance.
    Use ?ledger_account_id=<id> to focus on a single account."""
    report_type = "account_ledger"
    report_label = "Account Ledger"
    account_type = None


class ProfitLossView(_FinanceCustomView):
    """Profit & Loss — income vs expense per ledger account (group nature)."""
    report_type = "profit_loss"
    report_label = "Profit & Loss Statement"
    cache_ttl = 900

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        flat, page, limit, db_alias, cache_params = self._ctx(request)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        f = LedgerLineFilter(flat)
        qs = (
            JournalEntryLines.objects.using(db_alias)
            .filter(is_deleted=False,
                    ledger_account_id__ledger_group_id__nature__in=["Income", "Expense"])
        )
        qs = f.apply(qs)
        filters_applied = f.get_applied_filters()

        agg = (
            qs.values("ledger_account_id__name",
                      "ledger_account_id__ledger_group_id__nature")
            .annotate(d=Coalesce(Sum("debit"), ZERO), c=Coalesce(Sum("credit"), ZERO))
            .order_by("ledger_account_id__ledger_group_id__nature", "ledger_account_id__name")
        )
        income_total = expense_total = Decimal("0.00")
        rows = []
        for r in agg:
            nature = r["ledger_account_id__ledger_group_id__nature"]
            d = r["d"] or Decimal("0.00")
            c = r["c"] or Decimal("0.00")
            amount = (c - d) if nature == "Income" else (d - c)
            if nature == "Income":
                income_total += amount
            else:
                expense_total += amount
            rows.append({
                "account": r["ledger_account_id__name"] or "(Unassigned)",
                "nature": nature,
                "amount": amount,
            })

        net = income_total - expense_total
        summary = {
            "total_income": str(income_total),
            "total_expense": str(expense_total),
            "net_profit": str(net),
            "result": "Profit" if net >= 0 else "Loss",
        }
        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, resp.data, self.cache_ttl)
        return resp


class BalanceSheetView(_FinanceCustomView):
    """Balance Sheet — assets vs liabilities per ledger account (group nature)."""
    report_type = "balance_sheet"
    report_label = "Balance Sheet"
    cache_ttl = 900

    ASSET_NATURES = ["Asset", "AccountsReceivable"]
    LIABILITY_NATURES = ["Liability"]

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        flat, page, limit, db_alias, cache_params = self._ctx(request)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        natures = self.ASSET_NATURES + self.LIABILITY_NATURES
        f = LedgerLineFilter(flat)
        qs = (
            JournalEntryLines.objects.using(db_alias)
            .filter(is_deleted=False,
                    ledger_account_id__ledger_group_id__nature__in=natures)
        )
        qs = f.apply(qs)
        filters_applied = f.get_applied_filters()

        agg = (
            qs.values("ledger_account_id__name",
                      "ledger_account_id__ledger_group_id__nature")
            .annotate(d=Coalesce(Sum("debit"), ZERO), c=Coalesce(Sum("credit"), ZERO))
            .order_by("ledger_account_id__ledger_group_id__nature", "ledger_account_id__name")
        )
        asset_total = liability_total = Decimal("0.00")
        rows = []
        for r in agg:
            nature = r["ledger_account_id__ledger_group_id__nature"]
            d = r["d"] or Decimal("0.00")
            c = r["c"] or Decimal("0.00")
            is_asset = nature in self.ASSET_NATURES
            amount = (d - c) if is_asset else (c - d)
            if is_asset:
                asset_total += amount
            else:
                liability_total += amount
            rows.append({
                "account": r["ledger_account_id__name"] or "(Unassigned)",
                "side": "Asset" if is_asset else "Liability",
                "nature": nature,
                "amount": amount,
            })

        summary = {
            "total_assets": str(asset_total),
            "total_liabilities": str(liability_total),
            "difference": str(asset_total - liability_total),
        }
        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, resp.data, self.cache_ttl)
        return resp


class CashFlowView(_FinanceCustomView):
    """Cash Flow Forecast — week-by-week projected inflow vs outflow.

    Reuses the proven ai_features cash-flow service (single source of truth):
    inflow = unpaid sales invoices by due date, outflow = unpaid purchase
    invoices + pending expenses. This is a forward projection, not a formal
    operating/investing/financing statement (that needs activity tags we don't have).
    """
    report_type = "cash_flow"
    report_label = "Cash Flow Forecast"
    cache_ttl = 600

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        from apps.ai_features.services.cash_flow_forecast_service import get_cash_flow_forecast

        flat, page, limit, db_alias, cache_params = self._ctx(request)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        try:
            forecast_days = int(flat.get("forecast_days", 90))
        except (TypeError, ValueError):
            forecast_days = 90

        weekly, summary = get_cash_flow_forecast(forecast_days=forecast_days)
        rows = [{
            "week": w["week"],
            "period": f"{w['start_date']} to {w['end_date']}",
            "inflow": w["inflow"],
            "outflow_vendor": w["outflow_vendor"],
            "outflow_expense": w["outflow_expense"],
            "total_outflow": w["total_outflow"],
            "net": w["net"],
            "cumulative": w.get("cumulative", 0),
        } for w in weekly]

        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied={},
            page=page, limit=limit, total=total,
        )
        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, resp.data, self.cache_ttl)
        return resp


class JournalBookView(_FinanceCustomView):
    """Journal Book — MANUAL journal vouchers (JournalVoucher/JournalVoucherLine).

    Classic journal-book layout: lines grouped per voucher (debit line(s) first),
    voucher no/date shown ONCE per voucher (blanked on repeat lines). Distinct from
    the General Ledger (which reads JournalEntryLines). Reuses the legacy
    JournalBookReportView logic (entry_type→debit/credit, party = customer/vendor/
    employee). Labelled "manual vouchers" so it's not confused with the GL.
    """
    report_type = "journal_book"
    report_label = "Journal Book (Manual Vouchers)"
    cache_ttl = 300

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        flat, page, limit, db_alias, cache_params = self._ctx(request)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        f = JournalVoucherLineFilter(flat)
        qs = (
            JournalVoucherLine.objects.using(db_alias)
            .filter(journal_voucher_id__is_deleted=False)
            .select_related(
                "journal_voucher_id", "ledger_account_id",
                "customer_id", "vendor_id", "employee_id",
            )
        )
        qs = f.apply(qs)
        filters_applied = f.get_applied_filters()

        # Group lines under their voucher: newest voucher first, debit line(s)
        # before credit, stable by created_at. Built over the full set, then paged.
        from collections import OrderedDict
        lines = list(qs.order_by(
            "-journal_voucher_id__voucher_date", "journal_voucher_id__voucher_no",
            "entry_type", "created_at",
        ))
        groups = OrderedDict()
        for ln in lines:
            groups.setdefault(ln.journal_voucher_id_id, []).append(ln)

        rows = []
        total_debit = total_credit = Decimal("0.00")
        for vid, vlines in groups.items():
            v = vlines[0].journal_voucher_id
            narration = self._auto_narration(v, vlines)  # "(Being Journal Entry …)"
            for ln in vlines:
                party = self._line_party(ln)
                amount = ln.amount or Decimal("0.00")
                if ln.entry_type == "Debit":
                    total_debit += amount
                else:
                    total_credit += amount
                rows.append({
                    "journal_voucher_line_id": str(ln.journal_voucher_line_id),
                    "_vk": str(vid),  # internal key for per-page voucher grouping
                    "voucher_no": v.voucher_no if v else None,
                    "voucher_date": v.voucher_date if v else None,
                    "voucher_type": v.voucher_type if v else None,
                    "account": ln.ledger_account_id.name if ln.ledger_account_id else None,
                    "party": party,
                    "narration": narration,
                    "debit": amount if ln.entry_type == "Debit" else Decimal("0.00"),
                    "credit": amount if ln.entry_type == "Credit" else Decimal("0.00"),
                })

        summary = {
            "total_vouchers": len(groups),
            "total_lines": len(rows),
            "total_debit": str(total_debit),
            "total_credit": str(total_credit),
        }
        data, total = paginate_list(rows, page, limit)
        # Voucher no/date shown ONCE per voucher, blanked on the PAGE (after slicing)
        # so each page's first row keeps the voucher label across page boundaries.
        prev = object()
        for r in data:
            vk = r.pop("_vk", None)
            if vk == prev:
                r["voucher_no"] = ""
                r["voucher_date"] = None
            prev = vk
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, resp.data, self.cache_ttl)
        return resp

    @staticmethod
    def _line_party(ln):
        if ln.customer_id:
            return ln.customer_id.name
        if ln.vendor_id:
            return ln.vendor_id.name
        if ln.employee_id:
            return f"{ln.employee_id.first_name or ''} {ln.employee_id.last_name or ''}".strip() or None
        return None

    @classmethod
    def _auto_narration(cls, voucher, vlines):
        """Voucher narration in the legacy 'Being Journal Entry …' format —
        the user's custom narration if set, else auto-built from the lines
        (matches the old JournalBookReportView._build_particulars)."""
        if voucher and voucher.narration and voucher.narration.strip():
            return f"(Being Journal Entry {voucher.narration.strip()})"
        parts = []
        for ln in vlines:
            ledger = ln.ledger_account_id.name if ln.ledger_account_id else ""
            party = cls._line_party(ln)
            famt = f"₹{(ln.amount or Decimal('0.00')):,.2f}"
            if party:
                parts.append(f"{ledger} [ {party}]## {ln.entry_type} {famt}")
            elif ledger:
                parts.append(f"{ledger}## {ln.entry_type} {famt}")
        return f"(Being Journal Entry {' '.join(parts)})"


class _PartyLedgerView(_FinanceCustomView):
    """Customer / Vendor Ledger — that party's debit/credit lines from the ledger
    (JournalEntryLines filtered to the party), with a per-party running balance.
    Same running-balance engine as the Account Ledger; grouped & keyed by the
    party's UNIQUE id (names are not unique). Use ?customer_id= / ?vendor_id= to
    focus on one party.
    """
    party_field = None  # 'customer_id' or 'vendor_id'
    cache_ttl = 300

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        flat, page, limit, db_alias, cache_params = self._ctx(request)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        pf = self.party_field
        f = LedgerLineFilter(flat)
        qs = (
            JournalEntryLines.objects.using(db_alias)
            .filter(is_deleted=False, **{f"{pf}__isnull": False})
            .select_related("ledger_account_id", "journal_entry_id", pf)
            .annotate(_sd=Coalesce("journal_entry_id__entry_date", "entry_date"))
        )
        qs = f.apply(qs)
        filters_applied = f.get_applied_filters()

        # Group per party (alphabetical), then chronological; running balance keyed
        # on the party's UNIQUE id, computed over the full set before pagination.
        lines = list(qs.order_by(f"{pf}__name", pf, "_sd", "created_at"))
        rows, running = [], {}
        total_debit = total_credit = Decimal("0.00")
        for ln in lines:
            party_obj = getattr(ln, pf)
            party_key = getattr(ln, f"{pf}_id")
            d = ln.debit or Decimal("0.00")
            c = ln.credit or Decimal("0.00")
            running[party_key] = running.get(party_key, Decimal("0.00")) + d - c
            total_debit += d
            total_credit += c
            je = ln.journal_entry_id
            rows.append({
                "journal_entry_line_id": str(ln.journal_entry_line_id),
                "_pk": str(party_key),  # internal key for per-page grouping (popped below)
                # real transaction date if set, else the posting/recording date
                # (created_at) — like the legacy Account Ledger; never blank "—".
                "entry_date": (je.entry_date if je and je.entry_date else ln.entry_date)
                or (ln.created_at.date() if ln.created_at else None),
                "voucher_no": ln.voucher_no,
                "party": party_obj.name if party_obj else None,
                "account": ln.ledger_account_id.name if ln.ledger_account_id else None,
                "debit": d,
                "credit": c,
                "running_balance": running[party_key],
                "description": ln.description,
            })

        summary = {
            "total_parties": len(running),
            "total_lines": len(rows),
            "total_debit": str(total_debit),
            "total_credit": str(total_credit),
        }
        data, total = paginate_list(rows, page, limit)
        # Show the party name ONCE per group, blanked on repeats — but do it on the
        # PAGE (after slicing), so each page's first row always keeps its label even
        # when a party's lines straddle a page boundary.
        prev = object()
        for r in data:
            pk = r.pop("_pk", None)
            if pk == prev:
                r["party"] = ""
            prev = pk
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, resp.data, self.cache_ttl)
        return resp


class CustomerLedgerView(_PartyLedgerView):
    report_type = "customer_ledger"
    report_label = "Customer Ledger"
    party_field = "customer_id"


class VendorLedgerView(_PartyLedgerView):
    report_type = "vendor_ledger"
    report_label = "Vendor Ledger"
    party_field = "vendor_id"
