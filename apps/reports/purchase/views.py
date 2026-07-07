"""
Purchase Register — one endpoint, 13 view types (mirrors the Sale Register).

Field reality (verified against apps/purchase/models.py):
  PurchaseInvoiceOrders: invoice_no, invoice_date, supplier_invoice_no, voucher,
      tax_code, vendor_id, vendor_address_id, vendor_agent_id, order_status_id,
      item_value, dis_amt, tax_amount, round_off, total_amount, paid_amount,
      pending_amount, due_date, is_deleted
  PurchaseInvoiceItem: purchase_invoice_id, product_id, unit_options_id,
      quantity, rate, amount, discount, cgst, sgst, igst
  (NB: purchases have NO bill_type and items have NO stock_unit_id.)
"""

from decimal import Decimal

from django.db.models import Count, Sum, F, Value, DecimalField, Max
from django.db.models.functions import Coalesce, TruncDate, TruncMonth

from rest_framework.response import Response

from apps.reports.base.views import BaseReportView
from apps.reports.base.response import build_report_response, build_error_response
from apps.reports.base.pagination import (
    get_page_and_limit, paginate_queryset, paginate_list,
)
from apps.reports.purchase.filters import (
    PurchaseRegisterFilter, PurchaseRegisterItemFilter,
    PurchaseOrderFilter, PurchaseReturnFilter,
    BillPaymentFilter, VendorOutstandingFilter,
)
from apps.purchase.models import (
    PurchaseInvoiceOrders, PurchaseInvoiceItem,
    PurchaseOrders, PurchaseReturnOrders, BillPaymentTransactions,
)

ZERO = Value(Decimal("0.00"), output_field=DecimalField(max_digits=18, decimal_places=2))

REGISTER_TYPES = [
    "general",
    "detailed",
    "columnar_tax_wise",
    "columnar_product_group",
    "columnar_product_category",
    "columnar_product_brand",
    "columnar_hsn_wise",
    "cancelled",
    "daily_summary",
    "daily_payment_summary",
    "daily_tax_analysis",
    "monthly_summary",
    "monthly_payment_summary",
]

# Register types that query PurchaseInvoiceItem instead of PurchaseInvoiceOrders
ITEM_LEVEL_TYPES = {
    "detailed",
    "columnar_tax_wise",
    "columnar_product_group",
    "columnar_product_category",
    "columnar_product_brand",
    "columnar_hsn_wise",
    "daily_tax_analysis",
}


class PurchaseRegisterView(BaseReportView):
    report_type = "purchase_register"
    module = "purchase"
    cache_ttl = 300

    def get(self, request, *args, **kwargs):
        register_type = request.query_params.get("register_type", "general").strip().lower()
        if register_type not in REGISTER_TYPES:
            return build_error_response(
                message=f"Invalid register_type '{register_type}'.",
                errors={"valid_types": REGISTER_TYPES},
            )
        self._mode = register_type
        self.report_label = f"Purchase Register — {register_type.replace('_', ' ').title()}"
        return self._handle_report(request)

    # ── Queryset ──────────────────────────────────────────────────────────

    def get_queryset(self, request):
        if self._mode in ITEM_LEVEL_TYPES:
            return (
                PurchaseInvoiceItem.objects
                .filter(purchase_invoice_id__is_deleted=False)
                .select_related(
                    "purchase_invoice_id",
                    "purchase_invoice_id__vendor_id",
                    "purchase_invoice_id__vendor_address_id__city_id",
                    "purchase_invoice_id__order_status_id",
                    "purchase_invoice_id__vendor_agent_id",
                    "product_id",
                    "product_id__product_group_id",
                    "product_id__category_id",
                    "product_id__brand_id",
                    "unit_options_id",
                )
            )

        qs = (
            PurchaseInvoiceOrders.objects
            .filter(is_deleted=False)
            .select_related(
                "vendor_id",
                "vendor_address_id__city_id",
                "order_status_id",
                "vendor_agent_id",
            )
        )
        if self._mode == "cancelled":
            qs = qs.filter(order_status_id__status_name__iexact="cancelled")
        return qs

    # ── Filter class selection ────────────────────────────────────────────

    def _get_filter_instance(self, flat_params):
        if self._mode in ITEM_LEVEL_TYPES:
            return PurchaseRegisterItemFilter(flat_params)
        return PurchaseRegisterFilter(flat_params)

    # ── Summary KPIs ──────────────────────────────────────────────────────

    def get_summary(self, queryset):
        if self._mode in ITEM_LEVEL_TYPES:
            agg = queryset.aggregate(
                total_items=Count("purchase_invoice_item_id"),
                total_qty=Coalesce(Sum("quantity"), ZERO),
                total_amount=Coalesce(Sum("amount"), ZERO),
                total_discount=Coalesce(Sum("discount"), ZERO),
                total_cgst=Coalesce(Sum("cgst"), ZERO),
                total_sgst=Coalesce(Sum("sgst"), ZERO),
                total_igst=Coalesce(Sum("igst"), ZERO),
            )
            agg["total_tax"] = (
                (agg["total_cgst"] or Decimal("0"))
                + (agg["total_sgst"] or Decimal("0"))
                + (agg["total_igst"] or Decimal("0"))
            )
            return agg

        return queryset.aggregate(
            total_invoices=Count("purchase_invoice_id"),
            total_gross=Coalesce(Sum("item_value"), ZERO),
            total_discount=Coalesce(Sum("dis_amt"), ZERO),
            total_tax=Coalesce(Sum("tax_amount"), ZERO),
            total_net=Coalesce(Sum("total_amount"), ZERO),
            total_paid=Coalesce(Sum("paid_amount"), ZERO),
            total_pending=Coalesce(Sum("pending_amount"), ZERO),
        )

    # ── Serialization / aggregation ───────────────────────────────────────

    def serialize(self, queryset):
        mode = self._mode

        if mode in ("general", "cancelled"):
            return self._serialize_general(queryset)
        if mode == "detailed":
            return self._serialize_detailed(queryset)
        if mode == "columnar_tax_wise":
            return self._serialize_columnar_tax(queryset)
        if mode == "columnar_product_group":
            return self._serialize_grouped(queryset, "product_id__product_group_id__group_name")
        if mode == "columnar_product_category":
            return self._serialize_grouped(queryset, "product_id__category_id__category_name")
        if mode == "columnar_product_brand":
            return self._serialize_grouped(queryset, "product_id__brand_id__brand_name")
        if mode == "columnar_hsn_wise":
            return self._serialize_grouped(queryset, "product_id__hsn_code")
        if mode == "daily_summary":
            return self._serialize_daily_summary(queryset)
        if mode == "daily_payment_summary":
            return self._serialize_daily_payment(queryset)
        if mode == "daily_tax_analysis":
            return self._serialize_daily_tax(queryset)
        if mode == "monthly_summary":
            return self._serialize_monthly_summary(queryset)
        if mode == "monthly_payment_summary":
            return self._serialize_monthly_payment(queryset)
        return []

    # ── Private serialization helpers ─────────────────────────────────────

    def _serialize_general(self, queryset):
        rows = []
        for inv in queryset:
            rows.append({
                "purchase_invoice_id": str(inv.purchase_invoice_id),
                "invoice_no": inv.invoice_no,
                "invoice_date": inv.invoice_date,
                "supplier_invoice_no": inv.supplier_invoice_no,
                "voucher": inv.voucher,
                "vendor_name": inv.vendor_id.name if inv.vendor_id else None,
                "city": (
                    inv.vendor_address_id.city_id.city_name
                    if inv.vendor_address_id and inv.vendor_address_id.city_id
                    else None
                ),
                "vendor_agent": inv.vendor_agent_id.name if inv.vendor_agent_id else None,
                "item_value": inv.item_value,
                "dis_amt": inv.dis_amt,
                "tax_amount": inv.tax_amount,
                "round_off": inv.round_off,
                "total_amount": inv.total_amount,
                "paid_amount": inv.paid_amount,
                "pending_amount": inv.pending_amount,
                "due_date": inv.due_date,
                "status": inv.order_status_id.status_name if inv.order_status_id else None,
            })
        return rows

    def _serialize_detailed(self, queryset):
        rows = []
        for item in queryset:
            inv = item.purchase_invoice_id
            rows.append({
                "invoice_no": inv.invoice_no,
                "invoice_date": inv.invoice_date,
                "vendor_name": inv.vendor_id.name if inv.vendor_id else None,
                "product_name": item.product_id.name if item.product_id else None,
                "product_code": item.product_id.code if item.product_id else None,
                "hsn_code": item.product_id.hsn_code if item.product_id else None,
                "unit": item.unit_options_id.unit_name if item.unit_options_id else None,
                "quantity": item.quantity,
                "rate": item.rate,
                "amount": item.amount,
                "discount": item.discount,
                "cgst": item.cgst,
                "sgst": item.sgst,
                "igst": item.igst,
            })
        return rows

    def _serialize_columnar_tax(self, queryset):
        agg = (
            queryset
            .values(
                invoice_no=F("purchase_invoice_id__invoice_no"),
                invoice_date=F("purchase_invoice_id__invoice_date"),
                vendor_name=F("purchase_invoice_id__vendor_id__name"),
            )
            .annotate(
                taxable_amount=Coalesce(Sum("amount"), ZERO),
                cgst=Coalesce(Sum("cgst"), ZERO),
                sgst=Coalesce(Sum("sgst"), ZERO),
                igst=Coalesce(Sum("igst"), ZERO),
            )
            .annotate(
                total_tax=F("cgst") + F("sgst") + F("igst"),
                net_amount=F("taxable_amount") + F("cgst") + F("sgst") + F("igst"),
            )
            .order_by("invoice_date")
        )
        return list(agg)

    def _serialize_grouped(self, queryset, group_field):
        agg = (
            queryset
            .values(group_name=F(group_field))
            .annotate(
                total_qty=Coalesce(Sum("quantity"), ZERO),
                gross_amount=Coalesce(Sum("amount"), ZERO),
                total_discount=Coalesce(Sum("discount"), ZERO),
                cgst=Coalesce(Sum("cgst"), ZERO),
                sgst=Coalesce(Sum("sgst"), ZERO),
                igst=Coalesce(Sum("igst"), ZERO),
            )
            .annotate(net_amount=F("gross_amount") + F("cgst") + F("sgst") + F("igst"))
            .order_by("-gross_amount")
        )
        return list(agg)

    def _serialize_daily_summary(self, queryset):
        agg = (
            queryset
            .annotate(date=TruncDate("invoice_date"))
            .values("date")
            .annotate(
                invoice_count=Count("purchase_invoice_id"),
                gross_amount=Coalesce(Sum("item_value"), ZERO),
                total_discount=Coalesce(Sum("dis_amt"), ZERO),
                tax_amount=Coalesce(Sum("tax_amount"), ZERO),
                net_amount=Coalesce(Sum("total_amount"), ZERO),
            )
            .order_by("date")
        )
        return list(agg)

    def _serialize_daily_payment(self, queryset):
        agg = (
            queryset
            .annotate(date=TruncDate("invoice_date"))
            .values("date")
            .annotate(
                invoice_count=Count("purchase_invoice_id"),
                total_billed=Coalesce(Sum("total_amount"), ZERO),
                total_paid=Coalesce(Sum("paid_amount"), ZERO),
                total_pending=Coalesce(Sum("pending_amount"), ZERO),
            )
            .order_by("date")
        )
        return list(agg)

    def _serialize_daily_tax(self, queryset):
        agg = (
            queryset
            .annotate(date=TruncDate("purchase_invoice_id__invoice_date"))
            .values("date")
            .annotate(
                taxable_amount=Coalesce(Sum("amount"), ZERO),
                cgst=Coalesce(Sum("cgst"), ZERO),
                sgst=Coalesce(Sum("sgst"), ZERO),
                igst=Coalesce(Sum("igst"), ZERO),
            )
            .annotate(total_tax=F("cgst") + F("sgst") + F("igst"))
            .order_by("date")
        )
        return list(agg)

    def _serialize_monthly_summary(self, queryset):
        agg = (
            queryset
            .annotate(month=TruncMonth("invoice_date"))
            .values("month")
            .annotate(
                invoice_count=Count("purchase_invoice_id"),
                gross_amount=Coalesce(Sum("item_value"), ZERO),
                total_discount=Coalesce(Sum("dis_amt"), ZERO),
                tax_amount=Coalesce(Sum("tax_amount"), ZERO),
                net_amount=Coalesce(Sum("total_amount"), ZERO),
            )
            .order_by("month")
        )
        return [
            {**row, "month": row["month"].strftime("%Y-%m") if row["month"] else None}
            for row in agg
        ]

    def _serialize_monthly_payment(self, queryset):
        agg = (
            queryset
            .annotate(month=TruncMonth("invoice_date"))
            .values("month")
            .annotate(
                invoice_count=Count("purchase_invoice_id"),
                total_billed=Coalesce(Sum("total_amount"), ZERO),
                total_paid=Coalesce(Sum("paid_amount"), ZERO),
                total_pending=Coalesce(Sum("pending_amount"), ZERO),
            )
            .order_by("month")
        )
        return [
            {**row, "month": row["month"].strftime("%Y-%m") if row["month"] else None}
            for row in agg
        ]

    # ── Override _handle_report to wire filter selection + inject extra ───

    def _handle_report(self, request):
        from apps.reports.base.cache import get_cached, set_cached
        from rest_framework import status as drf_status

        params = dict(request.query_params)
        flat_params = {
            k: v[0] if isinstance(v, list) and len(v) == 1 else v
            for k, v in params.items()
        }

        page, limit = get_page_and_limit(request)
        db_alias = self._get_db_alias(request)

        cache_params = {**flat_params, "_page": page, "_limit": limit}
        if self.cache_ttl > 0:
            cached = get_cached(self.module, self.report_type, db_alias, cache_params)
            if cached is not None:
                return Response(cached, status=drf_status.HTTP_200_OK)

        queryset = self.get_queryset(request)
        if db_alias:
            queryset = queryset.using(db_alias)

        report_filter = self._get_filter_instance(flat_params)
        queryset = report_filter.apply(queryset)
        filters_applied = report_filter.get_applied_filters()

        summary = self.get_summary(queryset)

        # Aggregated modes paginate the already-summarised list; row modes paginate
        # the queryset before serialising (keeps memory low).
        if self._mode in (
            "columnar_tax_wise", "columnar_product_group", "columnar_product_category",
            "columnar_product_brand", "columnar_hsn_wise",
            "daily_summary", "daily_payment_summary", "daily_tax_analysis",
            "monthly_summary", "monthly_payment_summary",
        ):
            all_data = self.serialize(queryset)
            data, total = paginate_list(all_data, page, limit)
        else:
            paginated_qs, total = paginate_queryset(queryset, page, limit)
            data = self.serialize(paginated_qs)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
            extra={"register_types_available": REGISTER_TYPES},
        )

        if self.cache_ttl > 0:
            set_cached(
                self.module, self.report_type, db_alias,
                cache_params, response_obj.data, self.cache_ttl,
            )

        return response_obj


# ═════════════════════════════════════════════════════════════
# Iteration 3 — Pending Purchase Orders / Order Register / Return Register
# ═════════════════════════════════════════════════════════════

class PendingPurchaseOrdersView(BaseReportView):
    """Pending Purchase Orders — POs not yet completed."""
    report_type = "pending_purchase_orders"
    report_label = "Pending Purchase Orders"
    module = "purchase"
    filter_class = PurchaseOrderFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            PurchaseOrders.objects
            .filter(is_deleted=False)
            .exclude(order_status_id__status_name__iexact="completed")
            .select_related("vendor_id", "purchase_type_id", "order_status_id")
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_orders=Count("purchase_order_id"),
            total_value=Coalesce(Sum("total_amount"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for o in queryset:
            rows.append({
                "purchase_order_id": str(o.purchase_order_id),
                "order_no": o.order_no,
                "order_date": o.order_date,
                "delivery_date": o.delivery_date,
                "vendor_name": o.vendor_id.name if o.vendor_id else None,
                "purchase_type": o.purchase_type_id.name if o.purchase_type_id else None,
                "order_status": o.order_status_id.status_name if o.order_status_id else None,
                "item_value": o.item_value,
                "tax_amount": o.tax_amount,
                "total_amount": o.total_amount,
            })
        return rows


class PurchaseOrderRegisterView(BaseReportView):
    """Purchase Order Register — all purchase orders."""
    report_type = "purchase_order_register"
    report_label = "Purchase Order Register"
    module = "purchase"
    filter_class = PurchaseOrderFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            PurchaseOrders.objects
            .filter(is_deleted=False)
            .select_related("vendor_id", "purchase_type_id", "order_status_id")
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_orders=Count("purchase_order_id"),
            total_gross=Coalesce(Sum("item_value"), ZERO),
            total_tax=Coalesce(Sum("tax_amount"), ZERO),
            total_net=Coalesce(Sum("total_amount"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for o in queryset:
            rows.append({
                "purchase_order_id": str(o.purchase_order_id),
                "order_no": o.order_no,
                "order_date": o.order_date,
                "delivery_date": o.delivery_date,
                "vendor_name": o.vendor_id.name if o.vendor_id else None,
                "purchase_type": o.purchase_type_id.name if o.purchase_type_id else None,
                "order_status": o.order_status_id.status_name if o.order_status_id else None,
                "item_value": o.item_value,
                "tax_amount": o.tax_amount,
                "total_amount": o.total_amount,
            })
        return rows


class PurchaseReturnRegisterView(BaseReportView):
    """Purchase Return Register — all purchase returns."""
    report_type = "purchase_return_register"
    report_label = "Purchase Return Register"
    module = "purchase"
    filter_class = PurchaseReturnFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            PurchaseReturnOrders.objects
            .filter(is_deleted=False)
            .select_related("vendor_id", "order_status_id")
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_returns=Count("purchase_return_id"),
            total_gross=Coalesce(Sum("item_value"), ZERO),
            total_tax=Coalesce(Sum("tax_amount"), ZERO),
            total_net=Coalesce(Sum("total_amount"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for r in queryset:
            rows.append({
                "purchase_return_id": str(r.purchase_return_id),
                "return_no": r.return_no,
                "return_date": r.return_date,
                "vendor_name": r.vendor_id.name if r.vendor_id else None,
                "ref_no": r.ref_no,
                "return_reason": r.return_reason,
                "item_value": r.item_value,
                "tax_amount": r.tax_amount,
                "total_amount": r.total_amount,
                "order_status": r.order_status_id.status_name if r.order_status_id else None,
            })
        return rows


# ═════════════════════════════════════════════════════════════
# Iteration 4 — Bill Payments / Vendor Outstanding / Vendor Aging
# ═════════════════════════════════════════════════════════════

class BillPaymentRegisterView(BaseReportView):
    """Bill Payment Register — payments made to vendors (real-time, no cache)."""
    report_type = "bill_payment_register"
    report_label = "Bill Payment Register"
    module = "purchase"
    filter_class = BillPaymentFilter
    cache_ttl = 0

    def get_queryset(self, request):
        return (
            BillPaymentTransactions.objects
            .select_related("vendor", "purchase_invoice")
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_payments=Count("transaction_id"),
            total_amount=Coalesce(Sum("amount"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for p in queryset:
            rows.append({
                "transaction_id": str(p.transaction_id),
                "payment_receipt_no": p.payment_receipt_no,
                "payment_date": p.payment_date,
                "vendor_name": p.vendor.name if p.vendor else None,
                "invoice_no": p.purchase_invoice.invoice_no if p.purchase_invoice else None,
                "bill_no": p.bill_no,
                "payment_method": p.payment_method,
                "amount": p.amount,
                "payment_status": p.payment_status,
            })
        return rows


class VendorOutstandingView(BaseReportView):
    """
    Vendor Outstanding — purchase invoices with pending_amount > 0,
    one row per invoice with days overdue (real-time, no cache).
    """
    report_type = "vendor_outstanding"
    report_label = "Vendor Outstanding"
    module = "purchase"
    filter_class = VendorOutstandingFilter
    cache_ttl = 0

    def get_queryset(self, request):
        return (
            PurchaseInvoiceOrders.objects
            .filter(is_deleted=False, pending_amount__gt=0)
            .select_related("vendor_id", "order_status_id")
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_invoices=Count("purchase_invoice_id"),
            total_billed=Coalesce(Sum("total_amount"), ZERO),
            total_paid=Coalesce(Sum("paid_amount"), ZERO),
            total_pending=Coalesce(Sum("pending_amount"), ZERO),
        )

    def serialize(self, queryset):
        import datetime
        today = datetime.date.today()
        rows = []
        for inv in queryset:
            days_overdue = None
            if inv.due_date:
                delta = (today - inv.due_date).days
                days_overdue = delta if delta > 0 else 0
            rows.append({
                "purchase_invoice_id": str(inv.purchase_invoice_id),
                "invoice_no": inv.invoice_no,
                "invoice_date": inv.invoice_date,
                "due_date": inv.due_date,
                "vendor_name": inv.vendor_id.name if inv.vendor_id else None,
                "total_amount": inv.total_amount,
                "paid_amount": inv.paid_amount,
                "pending_amount": inv.pending_amount,
                "days_overdue": days_overdue,
                "status": inv.order_status_id.status_name if inv.order_status_id else None,
            })
        return rows


class VendorAgingView(BaseReportView):
    """
    Vendor Aging — outstanding purchase invoices bucketed by days overdue,
    grouped per vendor: current, 1-30, 31-60, 61-90, 91-120, 120+.
    Optional ?as_of_date=YYYY-MM-DD (defaults to today).
    """
    report_type = "vendor_aging"
    report_label = "Vendor Aging (Payables)"
    module = "purchase"
    cache_ttl = 900

    def get_queryset(self, request):
        return (
            PurchaseInvoiceOrders.objects
            .filter(is_deleted=False, pending_amount__gt=0)
            .select_related("vendor_id")
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_vendors=Count("vendor_id", distinct=True),
            total_outstanding=Coalesce(Sum("pending_amount"), ZERO),
        )

    def get(self, request, *args, **kwargs):
        return self._handle_report(request)

    def _handle_report(self, request):
        import datetime
        from apps.reports.base.cache import get_cached, set_cached
        from rest_framework import status as drf_status
        from apps.reports.base.filters import BaseReportFilter

        params = dict(request.query_params)
        flat_params = {
            k: v[0] if isinstance(v, list) and len(v) == 1 else v
            for k, v in params.items()
        }
        page, limit = get_page_and_limit(request)
        db_alias = self._get_db_alias(request)

        as_of_date = BaseReportFilter._parse_date(flat_params.get("as_of_date", "")) or datetime.date.today()

        cache_params = {**flat_params, "_page": page, "_limit": limit}
        if self.cache_ttl > 0:
            cached = get_cached(self.module, self.report_type, db_alias, cache_params)
            if cached is not None:
                return Response(cached, status=drf_status.HTTP_200_OK)

        queryset = self.get_queryset(request)
        if db_alias:
            queryset = queryset.using(db_alias)

        report_filter = VendorOutstandingFilter(flat_params)
        queryset = report_filter.apply(queryset)
        filters_applied = report_filter.get_applied_filters()
        filters_applied["as_of_date"] = str(as_of_date)

        summary = self.get_summary(queryset)

        vendor_map = {}
        for inv in queryset:
            vid = str(inv.vendor_id_id)
            vname = inv.vendor_id.name if inv.vendor_id else "Unknown"
            pending = inv.pending_amount or Decimal("0.00")
            if vid not in vendor_map:
                vendor_map[vid] = {
                    "vendor_id": vid, "vendor_name": vname,
                    "total_outstanding": Decimal("0.00"), "current": Decimal("0.00"),
                    "days_1_30": Decimal("0.00"), "days_31_60": Decimal("0.00"),
                    "days_61_90": Decimal("0.00"), "days_91_120": Decimal("0.00"),
                    "days_120_plus": Decimal("0.00"),
                }
            row = vendor_map[vid]
            row["total_outstanding"] += pending
            if not inv.due_date:
                row["current"] += pending
                continue
            days = (as_of_date - inv.due_date).days
            if days <= 0:
                row["current"] += pending
            elif days <= 30:
                row["days_1_30"] += pending
            elif days <= 60:
                row["days_31_60"] += pending
            elif days <= 90:
                row["days_61_90"] += pending
            elif days <= 120:
                row["days_91_120"] += pending
            else:
                row["days_120_plus"] += pending

        rows = sorted(vendor_map.values(), key=lambda r: r["total_outstanding"], reverse=True)
        data, total = paginate_list(rows, page, limit)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )

        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, response_obj.data, self.cache_ttl)

        return response_obj


# =============================================================
# Iteration 5 - Purchase Analysis (Product / Vendor) + GST Input Summary
# =============================================================

class _PurchaseAnalysisBase(BaseReportView):
    """Shared cache + Response plumbing for the grouped analysis reports."""
    cache_ttl = 600

    @staticmethod
    def _flat_params(request):
        # request.query_params is a QueryDict; dict() of it gives LIST values, e.g.
        # {'vendor_id': ['<uuid>']}. Flatten single-value lists so FK/UUID lookups
        # in the filter receive a plain string (this caused a 500 on ?vendor_id=).
        params = dict(request.query_params)
        return {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in params.items()}

    def _cached_response(self, request):
        from apps.reports.base.cache import get_cached
        db_alias = self._get_db_alias(request) or "default"
        cache_params = dict(request.query_params)
        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            # Always wrap in Response; returning a raw dict makes DRF 500 (CLAUDE gotcha 1).
            return Response(cached)
        return None

    def _store(self, request, payload):
        from apps.reports.base.cache import set_cached
        if self.cache_ttl > 0:
            db_alias = self._get_db_alias(request) or "default"
            set_cached(self.module, self.report_type, db_alias, dict(request.query_params), payload, self.cache_ttl)


class PurchaseAnalysisProductView(_PurchaseAnalysisBase):
    """Purchase Analysis by Product - qty, cost and tax per product."""
    report_type = "purchase_analysis_product"
    report_label = "Purchase Analysis - Product"
    module = "purchase"

    def get(self, request, *args, **kwargs):
        hit = self._cached_response(request)
        if hit is not None:
            return hit

        db_alias = self._get_db_alias(request) or "default"
        page, limit = get_page_and_limit(request)
        f = PurchaseRegisterItemFilter(self._flat_params(request))

        base_qs = (
            PurchaseInvoiceItem.objects.using(db_alias)
            .filter(purchase_invoice_id__is_deleted=False)
            .select_related("product_id", "purchase_invoice_id")
        )
        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        summary_agg = base_qs.aggregate(
            total_qty=Coalesce(Sum("quantity"), ZERO),
            total_revenue=Coalesce(Sum("amount"), ZERO),
            total_discount=Coalesce(Sum("discount"), ZERO),
        )

        agg = (
            base_qs
            .values("product_id", "product_id__name", "product_id__code")
            .annotate(
                total_qty=Coalesce(Sum("quantity"), ZERO),
                gross_amount=Coalesce(Sum("amount"), ZERO),
                total_discount=Coalesce(Sum("discount"), ZERO),
                cgst_sum=Coalesce(Sum("cgst"), ZERO),
                sgst_sum=Coalesce(Sum("sgst"), ZERO),
                igst_sum=Coalesce(Sum("igst"), ZERO),
            )
            .order_by("-gross_amount")
        )

        rows = []
        for r in agg:
            qty = r["total_qty"] or Decimal("0.00")
            gross = r["gross_amount"] or Decimal("0.00")
            tax = (r["cgst_sum"] or Decimal("0")) + (r["sgst_sum"] or Decimal("0")) + (r["igst_sum"] or Decimal("0"))
            rows.append({
                "product_id": str(r["product_id"]),
                "product_name": r["product_id__name"] or "",
                "product_code": r["product_id__code"],
                "total_qty": qty,
                "gross_amount": gross,
                "total_discount": r["total_discount"] or Decimal("0.00"),
                "total_tax": tax,
                "net_amount": gross + tax,
                "avg_rate": (gross / qty) if qty else Decimal("0.00"),
            })

        summary = {
            "total_products": len(rows),
            "total_qty": str(summary_agg["total_qty"]),
            "total_revenue": str(summary_agg["total_revenue"]),
            "total_discount": str(summary_agg["total_discount"]),
        }

        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        self._store(request, resp.data)
        return resp


class PurchaseAnalysisVendorView(_PurchaseAnalysisBase):
    """Purchase Analysis by Vendor - spend, paid and pending per vendor."""
    report_type = "purchase_analysis_vendor"
    report_label = "Purchase Analysis - Vendor"
    module = "purchase"

    def get(self, request, *args, **kwargs):
        hit = self._cached_response(request)
        if hit is not None:
            return hit

        db_alias = self._get_db_alias(request) or "default"
        page, limit = get_page_and_limit(request)
        f = PurchaseRegisterFilter(self._flat_params(request))

        base_qs = (
            PurchaseInvoiceOrders.objects.using(db_alias)
            .filter(is_deleted=False)
            .select_related("vendor_id")
        )
        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        summary_agg = base_qs.aggregate(
            total_invoices=Count("purchase_invoice_id"),
            total_amount=Coalesce(Sum("total_amount"), ZERO),
            total_paid=Coalesce(Sum("paid_amount"), ZERO),
            total_pending=Coalesce(Sum("pending_amount"), ZERO),
        )

        agg = (
            base_qs
            .values("vendor_id", "vendor_id__name")
            .annotate(
                total_invoices=Count("purchase_invoice_id"),
                total_amount=Coalesce(Sum("total_amount"), ZERO),
                total_paid=Coalesce(Sum("paid_amount"), ZERO),
                total_pending=Coalesce(Sum("pending_amount"), ZERO),
                last_invoice_date=Max("invoice_date"),
            )
            .order_by("-total_amount")
        )

        rows = []
        for r in agg:
            inv_count = r["total_invoices"] or 0
            total = r["total_amount"] or Decimal("0.00")
            rows.append({
                "vendor_id": str(r["vendor_id"]),
                "vendor_name": r["vendor_id__name"] or "",
                "total_invoices": inv_count,
                "total_amount": total,
                "total_paid": r["total_paid"] or Decimal("0.00"),
                "total_pending": r["total_pending"] or Decimal("0.00"),
                "avg_invoice_value": (total / inv_count) if inv_count else Decimal("0.00"),
                "last_invoice_date": r["last_invoice_date"],
            })

        summary = {
            "total_vendors": len(rows),
            "total_invoices": summary_agg["total_invoices"] or 0,
            "total_amount": str(summary_agg["total_amount"]),
            "total_paid": str(summary_agg["total_paid"]),
            "total_pending": str(summary_agg["total_pending"]),
        }

        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        self._store(request, resp.data)
        return resp


class GstInputSummaryView(_PurchaseAnalysisBase):
    """GST Input Summary - input tax credit (CGST/SGST/IGST) per purchase invoice."""
    report_type = "gst_input_summary"
    report_label = "GST Input Summary"
    module = "purchase"
    cache_ttl = 900

    def get(self, request, *args, **kwargs):
        hit = self._cached_response(request)
        if hit is not None:
            return hit

        db_alias = self._get_db_alias(request) or "default"
        page, limit = get_page_and_limit(request)
        f = PurchaseRegisterItemFilter(self._flat_params(request))

        base_qs = (
            PurchaseInvoiceItem.objects.using(db_alias)
            .filter(purchase_invoice_id__is_deleted=False)
            .select_related("purchase_invoice_id", "purchase_invoice_id__vendor_id")
        )
        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        agg = (
            base_qs
            .values(
                "purchase_invoice_id",
                "purchase_invoice_id__invoice_no",
                "purchase_invoice_id__invoice_date",
                "purchase_invoice_id__vendor_id__name",
            )
            .annotate(
                taxable_amount=Coalesce(Sum("amount"), ZERO),
                cgst=Coalesce(Sum("cgst"), ZERO),
                sgst=Coalesce(Sum("sgst"), ZERO),
                igst=Coalesce(Sum("igst"), ZERO),
            )
            .order_by("purchase_invoice_id__invoice_date")
        )

        rows = []
        for r in agg:
            cgst = r["cgst"] or Decimal("0.00")
            sgst = r["sgst"] or Decimal("0.00")
            igst = r["igst"] or Decimal("0.00")
            taxable = r["taxable_amount"] or Decimal("0.00")
            total_tax = cgst + sgst + igst
            rows.append({
                "invoice_no": r["purchase_invoice_id__invoice_no"] or "",
                "invoice_date": r["purchase_invoice_id__invoice_date"],
                "vendor_name": r["purchase_invoice_id__vendor_id__name"] or "",
                "taxable_amount": taxable,
                "cgst": cgst, "sgst": sgst, "igst": igst,
                "total_tax": total_tax,
                "net_amount": taxable + total_tax,
            })

        summary = {
            "total_invoices": len(rows),
            "total_taxable": str(sum(r["taxable_amount"] for r in rows)),
            "total_cgst": str(sum(r["cgst"] for r in rows)),
            "total_sgst": str(sum(r["sgst"] for r in rows)),
            "total_igst": str(sum(r["igst"] for r in rows)),
            "total_tax": str(sum(r["total_tax"] for r in rows)),
        }

        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        self._store(request, resp.data)
        return resp


class PurchasePriceVarianceView(_PurchaseAnalysisBase):
    """Purchase Price Variance — overspend vs the best available vendor rate.

    REUSES the proven `price_variance` Smart Insight (single source of truth, like
    Cash Flow) so the report and the dashboard always show the same numbers
    (CLAUDE.md §4B / flow.md). PPV here = (your avg rate − best vendor rate) × qty.
    """
    report_type = "purchase_price_variance"
    report_label = "Purchase Price Variance"
    module = "purchase"
    cache_ttl = 900

    def get(self, request, *args, **kwargs):
        from apps.ai_features.services.price_variance_service import get_price_variance

        hit = self._cached_response(request)
        if hit is not None:
            return hit

        flat = self._flat_params(request)
        page, limit = get_page_and_limit(request)
        from_date = flat.get("from_date") or None
        to_date = flat.get("to_date") or None

        results, summary = get_price_variance(from_date=from_date, to_date=to_date)
        rows = []
        for r in results:
            p, v = r["product"], r["vendor"]
            rows.append({
                "product_id": str(p.product_id),
                "product_name": p.name,
                "product_code": p.code,
                "vendor_name": v.name,
                "avg_rate": r["avg_rate"],
                "best_rate": r["best_rate"],
                "latest_rate": r["latest_rate"],
                "total_qty": r["total_qty"],
                "overspend": r["overspend"],
                "purchase_count": r["purchase_count"],
                "trend": r["trend"],
            })

        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied={},
            page=page, limit=limit, total=total,
        )
        self._store(request, resp.data)
        return resp


class StockReplenishmentView(_PurchaseAnalysisBase):
    """Stock Replenishment — items at/below reorder level needing a purchase.

    REUSES the `auto_purchase_order` reorder-suggestion Smart Insight (single
    source of truth) — same below-min logic + best-vendor + qty as the dashboard.
    """
    report_type = "stock_replenishment"
    report_label = "Stock Replenishment"
    module = "purchase"
    cache_ttl = 600

    def get(self, request, *args, **kwargs):
        from apps.ai_features.services.auto_purchase_order_service import get_reorder_suggestions

        hit = self._cached_response(request)
        if hit is not None:
            return hit

        page, limit = get_page_and_limit(request)
        results = get_reorder_suggestions()
        rows = []
        for r in results:
            p = r["product"]
            rows.append({
                "product_id": str(p.product_id),
                "product_name": p.name,
                "product_code": p.code,
                "current_balance": r["current_balance"],
                "minimum_level": r["minimum_level"],
                "maximum_level": r["maximum_level"],
                "shortage": r["shortage"],
                "reorder_qty": r["reorder_qty"],
                "best_vendor_name": r["best_vendor_name"],
                "latest_rate": r["latest_rate"],
                "estimated_cost": r["estimated_cost"],
            })

        summary = {
            "total_items": len(rows),
            "total_estimated_cost": str(sum(Decimal(str(r["estimated_cost"])) for r in rows)),
        }

        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied={},
            page=page, limit=limit, total=total,
        )
        self._store(request, resp.data)
        return resp


class VendorPerformanceView(_PurchaseAnalysisBase):
    """Vendor Performance scorecard — price / delivery / quality per vendor.

    REUSES the `best_vendor` Smart Insight's KPIs (single source of truth) and
    aggregates them per vendor, so the scorecard and the dashboard always agree.
    Delivery / quality are null ("no data") when that KPI can't be measured — never
    faked to a neutral 50 (flow.md).
    """
    report_type = "vendor_performance"
    report_label = "Vendor Performance"
    module = "purchase"
    cache_ttl = 900

    def get(self, request, *args, **kwargs):
        from apps.ai_features.services.best_vendor_service import get_best_vendors

        hit = self._cached_response(request)
        if hit is not None:
            return hit

        page, limit = get_page_and_limit(request)
        bv = get_best_vendors()

        # Roll the per-(product,vendor) scores up to one row per vendor.
        vendors = {}
        for prod in bv:
            for e in prod["vendors"]:
                v = e["vendor"]
                vid = str(v.vendor_id)
                a = vendors.setdefault(vid, {
                    "vendor": v, "price": [], "delivery": [], "quality": [],
                    "total": [], "products": 0, "returns": 0.0,
                })
                a["products"] += 1
                a["price"].append(e["price_score"])
                if e["delivery_score"] is not None:
                    a["delivery"].append(e["delivery_score"])
                if e["quality_score"] is not None:
                    a["quality"].append(e["quality_score"])
                if e["total_score"] is not None:
                    a["total"].append(e["total_score"])
                a["returns"] += float(e["return_qty"] or 0)

        def avg(lst):
            return round(sum(lst) / len(lst), 2) if lst else None

        rows = []
        for vid, a in vendors.items():
            rows.append({
                "vendor_id": vid,
                "vendor_name": a["vendor"].name,
                "products_supplied": a["products"],
                "price_score": avg(a["price"]),
                "delivery_score": avg(a["delivery"]),
                "quality_score": avg(a["quality"]),
                "overall_score": avg(a["total"]),
                "total_returns": round(a["returns"], 2),
            })
        rows.sort(key=lambda r: -(r["overall_score"] or 0))

        summary = {"total_vendors": len(rows)}
        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied={},
            page=page, limit=limit, total=total,
        )
        self._store(request, resp.data)
        return resp
