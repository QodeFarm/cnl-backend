from decimal import Decimal

from django.db.models import (
    Count, Sum, F, Q, Value, DecimalField, CharField
)
from django.db.models.functions import (
    Coalesce, TruncDate, TruncMonth
)

from rest_framework.response import Response

from apps.reports.base.views import BaseReportView
from apps.reports.base.response import build_report_response, build_error_response
from apps.reports.base.pagination import get_page_and_limit, paginate_queryset, paginate_list
from apps.reports.sales.filters import (
    SalesRegisterFilter, SalesRegisterItemFilter,
    SaleOrderFilter, DeliveryChallanFilter,
    SaleReturnFilter, CreditDebitNoteFilter,
    PaymentReminderFilter, CustomerAgingFilter,
    NewCustomersFilter, SalesOrderAnalysisFilter,
)
from apps.reports.sales.serializers import (
    SaleRegisterGeneralSerializer,
    SaleRegisterDetailedSerializer,
    SaleRegisterColumnarTaxSerializer,
    SaleRegisterGroupedSerializer,
    SaleRegisterDailySummarySerializer,
    SaleRegisterDailyPaymentSerializer,
    SaleRegisterDailyTaxSerializer,
    SaleRegisterMonthlySummarySerializer,
    SaleRegisterMonthlyPaymentSerializer,
    SaleOrderRegisterSerializer,
    DeliveryChallanRegisterSerializer,
    SaleReturnRegisterSerializer,
    CreditDebitNoteRegisterSerializer,
    PaymentReminderDetailSerializer,
    PaymentReminderSummarySerializer,
    CustomerAgingSerializer,
    NewCustomerSerializer,
    NoSalesCustomerSerializer,
    LimitExceededCustomerSerializer,
    SalesOrderAnalysisSerializer,
    ProductSalesAnalysisSerializer,
    CustomerSalesAnalysisSerializer,
    SalespersonAnalysisSerializer,
    ProfitMarginSerializer,
    SalesTrendSerializer,
    GstSummarySerializer,
)
from apps.customer.models import Customer
from apps.sales.models import (
    SaleInvoiceOrders, SaleInvoiceItems,
    SaleOrder, DeliveryChallans, SaleReturnOrders,
    SaleCreditNotes, SaleDebitNotes,
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

# Register types that query SaleInvoiceItems instead of SaleInvoiceOrders
ITEM_LEVEL_TYPES = {
    "detailed",
    "columnar_tax_wise",
    "columnar_product_group",
    "columnar_product_category",
    "columnar_product_brand",
    "columnar_hsn_wise",
    "daily_tax_analysis",
}


class SalesRegisterView(BaseReportView):
    report_type = "sales_register"
    module = "sales"
    cache_ttl = 300

    def get(self, request, *args, **kwargs):
        register_type = request.query_params.get("register_type", "general").strip().lower()
        if register_type not in REGISTER_TYPES:
            return build_error_response(
                message=f"Invalid register_type '{register_type}'.",
                errors={"valid_types": REGISTER_TYPES},
            )
        self._mode = register_type
        self.report_label = f"Sale Register — {register_type.replace('_', ' ').title()}"
        return self._handle_report(request)

    # ── Queryset ──────────────────────────────────────────────────────────

    def get_queryset(self, request):
        if self._mode in ITEM_LEVEL_TYPES:
            return (
                SaleInvoiceItems.objects
                .filter(sale_invoice_id__is_deleted=False)
                .select_related(
                    "sale_invoice_id",
                    "sale_invoice_id__customer_id",
                    "sale_invoice_id__customer_address_id__city_id",
                    "sale_invoice_id__order_status_id",
                    "sale_invoice_id__order_salesman_id",
                    "product_id",
                    "product_id__product_group_id",
                    "product_id__category_id",
                    "product_id__brand_id",
                    "unit_options_id",
                    "stock_unit_id",
                )
            )

        qs = (
            SaleInvoiceOrders.objects
            .filter(is_deleted=False)
            .select_related(
                "customer_id",
                "customer_address_id__city_id",
                "order_status_id",
                "order_salesman_id",
            )
        )
        if self._mode == "cancelled":
            qs = qs.filter(order_status_id__status_name__iexact="cancelled")
        return qs

    # ── Filter class selection ────────────────────────────────────────────

    def _get_filter_instance(self, flat_params):
        if self._mode in ITEM_LEVEL_TYPES:
            return SalesRegisterItemFilter(flat_params)
        return SalesRegisterFilter(flat_params)

    # ── Summary KPIs ──────────────────────────────────────────────────────

    def get_summary(self, queryset):
        if self._mode in ITEM_LEVEL_TYPES:
            agg = queryset.aggregate(
                total_items=Count("sale_invoice_item_id"),
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

        agg = queryset.aggregate(
            total_invoices=Count("sale_invoice_id"),
            total_gross=Coalesce(Sum("item_value"), ZERO),
            total_discount=Coalesce(Sum("dis_amt"), ZERO),
            total_tax=Coalesce(Sum("tax_amount"), ZERO),
            total_net=Coalesce(Sum("total_amount"), ZERO),
            total_paid=Coalesce(Sum("paid_amount"), ZERO),
            total_pending=Coalesce(Sum("pending_amount"), ZERO),
        )
        return agg

    # ── Serialization / aggregation ───────────────────────────────────────

    def serialize(self, queryset):
        mode = self._mode

        if mode == "general" or mode == "cancelled":
            return self._serialize_general(queryset)

        if mode == "detailed":
            return self._serialize_detailed(queryset)

        if mode == "columnar_tax_wise":
            return self._serialize_columnar_tax(queryset)

        if mode == "columnar_product_group":
            return self._serialize_grouped(
                queryset,
                group_field="product_id__product_group_id__group_name",
                group_label="product_group",
            )

        if mode == "columnar_product_category":
            return self._serialize_grouped(
                queryset,
                group_field="product_id__category_id__category_name",
                group_label="product_category",
            )

        if mode == "columnar_product_brand":
            return self._serialize_grouped(
                queryset,
                group_field="product_id__brand_id__brand_name",
                group_label="product_brand",
            )

        if mode == "columnar_hsn_wise":
            return self._serialize_grouped(
                queryset,
                group_field="product_id__hsn_code",
                group_label="hsn_code",
            )

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
                "sale_invoice_id": str(inv.sale_invoice_id),
                "invoice_no": inv.invoice_no,
                "invoice_date": inv.invoice_date,
                "bill_type": inv.bill_type,
                "customer_name": inv.customer_id.name if inv.customer_id else None,
                "city": (
                    inv.customer_address_id.city_id.city_name
                    if inv.customer_address_id and inv.customer_address_id.city_id
                    else None
                ),
                "salesperson": (
                    inv.order_salesman_id.name if inv.order_salesman_id else None
                ),
                "item_value": inv.item_value,
                "dis_amt": inv.dis_amt,
                "tax_amount": inv.tax_amount,
                "round_off": inv.round_off,
                "total_amount": inv.total_amount,
                "paid_amount": inv.paid_amount,
                "pending_amount": inv.pending_amount,
                "due_date": inv.due_date,
                "status": (
                    inv.order_status_id.status_name if inv.order_status_id else None
                ),
            })
        return rows

    def _serialize_detailed(self, queryset):
        rows = []
        for item in queryset:
            inv = item.sale_invoice_id
            unit = None
            if item.unit_options_id:
                unit = item.unit_options_id.unit_name
            elif item.stock_unit_id:
                unit = item.stock_unit_id.stock_unit_name
            rows.append({
                "invoice_no": inv.invoice_no,
                "invoice_date": inv.invoice_date,
                "bill_type": inv.bill_type,
                "customer_name": inv.customer_id.name if inv.customer_id else None,
                "product_name": item.product_id.name if item.product_id else None,
                "product_code": item.product_id.code if item.product_id else None,
                "hsn_code": item.product_id.hsn_code if item.product_id else None,
                "unit": unit,
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
        # Group by invoice — aggregate tax columns
        # Split into two .annotate() calls: aliases (cgst/sgst/igst) defined first,
        # then computed fields use F() refs to avoid "cgst is an aggregate" error.
        agg = (
            queryset
            .values(
                invoice_no=F("sale_invoice_id__invoice_no"),
                invoice_date=F("sale_invoice_id__invoice_date"),
                customer_name=F("sale_invoice_id__customer_id__name"),
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

    def _serialize_grouped(self, queryset, group_field, group_label):
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
            .annotate(
                net_amount=F("gross_amount") + F("cgst") + F("sgst") + F("igst"),
            )
            .order_by("-gross_amount")
        )
        return list(agg)

    def _serialize_daily_summary(self, queryset):
        agg = (
            queryset
            .annotate(date=TruncDate("invoice_date"))
            .values("date")
            .annotate(
                invoice_count=Count("sale_invoice_id"),
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
                invoice_count=Count("sale_invoice_id"),
                total_billed=Coalesce(Sum("total_amount"), ZERO),
                total_collected=Coalesce(Sum("paid_amount"), ZERO),
                total_pending=Coalesce(Sum("pending_amount"), ZERO),
            )
            .order_by("date")
        )
        return list(agg)

    def _serialize_daily_tax(self, queryset):
        agg = (
            queryset
            .annotate(date=TruncDate("sale_invoice_id__invoice_date"))
            .values("date")
            .annotate(
                taxable_amount=Coalesce(Sum("amount"), ZERO),
                cgst=Coalesce(Sum("cgst"), ZERO),
                sgst=Coalesce(Sum("sgst"), ZERO),
                igst=Coalesce(Sum("igst"), ZERO),
            )
            .annotate(
                total_tax=F("cgst") + F("sgst") + F("igst"),
            )
            .order_by("date")
        )
        return list(agg)

    def _serialize_monthly_summary(self, queryset):
        agg = (
            queryset
            .annotate(month=TruncMonth("invoice_date"))
            .values("month")
            .annotate(
                invoice_count=Count("sale_invoice_id"),
                gross_amount=Coalesce(Sum("item_value"), ZERO),
                total_discount=Coalesce(Sum("dis_amt"), ZERO),
                tax_amount=Coalesce(Sum("tax_amount"), ZERO),
                net_amount=Coalesce(Sum("total_amount"), ZERO),
            )
            .order_by("month")
        )
        rows = []
        for row in agg:
            rows.append({
                **row,
                "month": row["month"].strftime("%Y-%m") if row["month"] else None,
            })
        return rows

    def _serialize_monthly_payment(self, queryset):
        agg = (
            queryset
            .annotate(month=TruncMonth("invoice_date"))
            .values("month")
            .annotate(
                invoice_count=Count("sale_invoice_id"),
                total_billed=Coalesce(Sum("total_amount"), ZERO),
                total_collected=Coalesce(Sum("paid_amount"), ZERO),
                total_pending=Coalesce(Sum("pending_amount"), ZERO),
            )
            .order_by("month")
        )
        rows = []
        for row in agg:
            rows.append({
                **row,
                "month": row["month"].strftime("%Y-%m") if row["month"] else None,
            })
        return rows

    # ── Override _handle_report to wire filter selection + inject extra ───

    def _handle_report(self, request):
        params = dict(request.query_params)
        flat_params = {
            k: v[0] if isinstance(v, list) and len(v) == 1 else v
            for k, v in params.items()
        }

        page, limit = get_page_and_limit(request)
        db_alias = self._get_db_alias(request)

        from apps.reports.base.cache import get_cached, set_cached
        from rest_framework import status as drf_status
        from rest_framework.response import Response

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

        # For aggregated modes (grouped / daily / monthly) pagination happens on
        # the already-aggregated list returned by serialize(); for row-level modes
        # we paginate the queryset before serializing to keep memory low.
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
# Step 3 — Pending Registers
# ═════════════════════════════════════════════════════════════

class PendingSaleOrdersView(BaseReportView):
    """Pending Sale Orders — orders not yet completed."""
    report_type = "pending_sale_orders"
    report_label = "Pending Sale Orders"
    module = "sales"
    filter_class = SaleOrderFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            SaleOrder.objects
            .filter(is_deleted=False)
            .exclude(order_status_id__status_name__iexact="completed")
            .select_related(
                "customer_id",
                "sale_type_id",
                "flow_status_id",
                "order_status_id",
            )
        )

    def get_summary(self, queryset):
        from django.db.models import Count, Sum
        return queryset.aggregate(
            total_orders=Count("sale_order_id"),
            total_value=Coalesce(Sum("total_amount"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for obj in queryset:
            rows.append({
                "sale_order_id": str(obj.sale_order_id),
                "order_no": obj.order_no,
                "order_date": obj.order_date,
                "delivery_date": obj.delivery_date,
                "customer_name": obj.customer_id.name if obj.customer_id else None,
                "sale_type": obj.sale_type_id.name if obj.sale_type_id else None,
                "flow_status": obj.flow_status_id.flow_status_name if obj.flow_status_id else None,
                "order_status": obj.order_status_id.status_name if obj.order_status_id else None,
                "item_value": obj.item_value,
                "tax_amount": obj.tax_amount,
                "total_amount": obj.total_amount,
            })
        return rows


class PendingChallansView(BaseReportView):
    """Pending Sale Challans — challans not yet converted to invoice."""
    report_type = "pending_challans"
    report_label = "Pending Sale Challans"
    module = "sales"
    filter_class = DeliveryChallanFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            DeliveryChallans.objects
            .filter(is_deleted=False, is_converted=False)
            .select_related(
                "customer_id",
                "sale_order_id",
                "order_salesman_id",
                "order_status_id",
            )
        )

    def get_summary(self, queryset):
        from django.db.models import Count, Sum
        return queryset.aggregate(
            total_challans=Count("delivery_challan_id"),
            total_value=Coalesce(Sum("total_amount"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for obj in queryset:
            rows.append({
                "delivery_challan_id": str(obj.delivery_challan_id),
                "challan_no": obj.challan_no,
                "challan_date": obj.challan_date,
                "customer_name": obj.customer_id.name if obj.customer_id else None,
                "linked_order_no": obj.sale_order_id.order_no if obj.sale_order_id else None,
                "salesperson": obj.order_salesman_id.name if obj.order_salesman_id else None,
                "item_value": obj.item_value,
                "tax_amount": obj.tax_amount,
                "total_amount": obj.total_amount,
                "is_converted": obj.is_converted,
                "order_status": obj.order_status_id.status_name if obj.order_status_id else None,
            })
        return rows


# ═════════════════════════════════════════════════════════════
# Step 3 — Trading Registers
# ═════════════════════════════════════════════════════════════

class SaleOrderRegisterView(BaseReportView):
    """Sale Order Register — all orders."""
    report_type = "sale_order_register"
    report_label = "Sale Order Register"
    module = "sales"
    filter_class = SaleOrderFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            SaleOrder.objects
            .filter(is_deleted=False)
            .select_related(
                "customer_id",
                "sale_type_id",
                "flow_status_id",
                "order_status_id",
            )
        )

    def get_summary(self, queryset):
        from django.db.models import Count, Sum
        return queryset.aggregate(
            total_orders=Count("sale_order_id"),
            total_gross=Coalesce(Sum("item_value"), ZERO),
            total_tax=Coalesce(Sum("tax_amount"), ZERO),
            total_net=Coalesce(Sum("total_amount"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for obj in queryset:
            rows.append({
                "sale_order_id": str(obj.sale_order_id),
                "order_no": obj.order_no,
                "order_date": obj.order_date,
                "delivery_date": obj.delivery_date,
                "customer_name": obj.customer_id.name if obj.customer_id else None,
                "sale_type": obj.sale_type_id.name if obj.sale_type_id else None,
                "flow_status": obj.flow_status_id.flow_status_name if obj.flow_status_id else None,
                "order_status": obj.order_status_id.status_name if obj.order_status_id else None,
                "item_value": obj.item_value,
                "tax_amount": obj.tax_amount,
                "total_amount": obj.total_amount,
            })
        return rows


class SaleChallanRegisterView(BaseReportView):
    """Sale Challan Register — all challans."""
    report_type = "sale_challan_register"
    report_label = "Sale Challan Register"
    module = "sales"
    filter_class = DeliveryChallanFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            DeliveryChallans.objects
            .filter(is_deleted=False)
            .select_related(
                "customer_id",
                "sale_order_id",
                "order_salesman_id",
                "order_status_id",
            )
        )

    def get_summary(self, queryset):
        from django.db.models import Count, Sum
        return queryset.aggregate(
            total_challans=Count("delivery_challan_id"),
            total_converted=Count("delivery_challan_id", filter=Q(is_converted=True)),
            total_value=Coalesce(Sum("total_amount"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for obj in queryset:
            rows.append({
                "delivery_challan_id": str(obj.delivery_challan_id),
                "challan_no": obj.challan_no,
                "challan_date": obj.challan_date,
                "customer_name": obj.customer_id.name if obj.customer_id else None,
                "linked_order_no": obj.sale_order_id.order_no if obj.sale_order_id else None,
                "salesperson": obj.order_salesman_id.name if obj.order_salesman_id else None,
                "item_value": obj.item_value,
                "tax_amount": obj.tax_amount,
                "total_amount": obj.total_amount,
                "is_converted": obj.is_converted,
                "order_status": obj.order_status_id.status_name if obj.order_status_id else None,
            })
        return rows


class SaleReturnRegisterView(BaseReportView):
    """Sale Return Register — all returns."""
    report_type = "sale_return_register"
    report_label = "Sale Return Register"
    module = "sales"
    filter_class = SaleReturnFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            SaleReturnOrders.objects
            .filter(is_deleted=False)
            .select_related(
                "customer_id",
                "sale_invoice_id",
                "order_status_id",
            )
        )

    def get_summary(self, queryset):
        from django.db.models import Count, Sum
        return queryset.aggregate(
            total_returns=Count("sale_return_id"),
            total_gross=Coalesce(Sum("item_value"), ZERO),
            total_tax=Coalesce(Sum("tax_amount"), ZERO),
            total_net=Coalesce(Sum("total_amount"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for obj in queryset:
            rows.append({
                "sale_return_id": str(obj.sale_return_id),
                "return_no": obj.return_no,
                "return_date": obj.return_date,
                "bill_type": obj.bill_type,
                "customer_name": obj.customer_id.name if obj.customer_id else None,
                "against_invoice_no": (
                    obj.sale_invoice_id.invoice_no if obj.sale_invoice_id else None
                ),
                "return_reason": obj.return_reason,
                "item_value": obj.item_value,
                "tax_amount": obj.tax_amount,
                "total_amount": obj.total_amount,
                "order_status": obj.order_status_id.status_name if obj.order_status_id else None,
            })
        return rows


class CreditDebitNoteRegisterView(BaseReportView):
    """
    Credit / Debit Note Register — combines SaleCreditNotes + SaleDebitNotes.
    Optional filter: ?note_type=credit  or  ?note_type=debit
    """
    report_type = "credit_debit_note_register"
    report_label = "Credit / Debit Note Register"
    module = "sales"
    cache_ttl = 300

    def get_queryset(self, request):
        # Not used directly — overridden in _handle_report
        return SaleCreditNotes.objects.none()

    def get_summary(self, queryset):
        return {}

    def serialize(self, queryset):
        return []

    def get(self, request, *args, **kwargs):
        return self._handle_report(request)

    def _handle_report(self, request):
        from apps.reports.base.cache import get_cached, set_cached
        from rest_framework import status as drf_status
        from rest_framework.response import Response

        params = dict(request.query_params)
        flat_params = {
            k: v[0] if isinstance(v, list) and len(v) == 1 else v
            for k, v in params.items()
        }
        page, limit = get_page_and_limit(request)
        db_alias = self._get_db_alias(request)
        note_type = flat_params.get("note_type", "").strip().lower()  # 'credit', 'debit', or ''

        cache_params = {**flat_params, "_page": page, "_limit": limit}
        if self.cache_ttl > 0:
            cached = get_cached(self.module, self.report_type, db_alias, cache_params)
            if cached is not None:
                return Response(cached, status=drf_status.HTTP_200_OK)

        # Filter each note type by its OWN date column so the date/period filter
        # matches the date shown in the report (Bug C fix). Credit notes carry
        # credit_date; debit notes carry debit_date.
        credit_filter = CreditDebitNoteFilter(flat_params)
        credit_filter.date_field = "credit_date"
        debit_filter = CreditDebitNoteFilter(flat_params)
        debit_filter.date_field = "debit_date"

        rows = []
        total_credit = Decimal("0.00")
        total_debit = Decimal("0.00")

        if note_type != "debit":
            credit_qs = (
                SaleCreditNotes.objects
                .filter(is_deleted=False)
                .select_related("customer_id", "sale_invoice_id", "order_status_id")
            )
            credit_qs = credit_filter.apply(credit_qs)
            for obj in credit_qs:
                rows.append({
                    "note_id": str(obj.credit_note_id),
                    "note_number": obj.credit_note_number,
                    "note_type": "Credit",
                    "note_date": obj.credit_date,
                    "customer_name": obj.customer_id.name if obj.customer_id else None,
                    "against_invoice_no": (
                        obj.sale_invoice_id.invoice_no if obj.sale_invoice_id else None
                    ),
                    "reason": obj.reason,
                    "total_amount": obj.total_amount,
                    "order_status": obj.order_status_id.status_name if obj.order_status_id else None,
                })
                total_credit += obj.total_amount or Decimal("0.00")

        if note_type != "credit":
            debit_qs = (
                SaleDebitNotes.objects
                .filter(is_deleted=False)
                .select_related("customer_id", "sale_invoice_id", "order_status_id")
            )
            debit_qs = debit_filter.apply(debit_qs)
            for obj in debit_qs:
                rows.append({
                    "note_id": str(obj.debit_note_id),
                    "note_number": obj.debit_note_number,
                    "note_type": "Debit",
                    "note_date": obj.debit_date,
                    "customer_name": obj.customer_id.name if obj.customer_id else None,
                    "against_invoice_no": (
                        obj.sale_invoice_id.invoice_no if obj.sale_invoice_id else None
                    ),
                    "reason": obj.reason,
                    "total_amount": obj.total_amount,
                    "order_status": obj.order_status_id.status_name if obj.order_status_id else None,
                })
                total_debit += obj.total_amount or Decimal("0.00")

        # Sort combined list by date descending
        rows.sort(key=lambda r: r["note_date"] or "", reverse=True)

        summary = {
            "total_records": len(rows),
            "total_credit_amount": str(total_credit),
            "total_debit_amount": str(total_debit),
            "total_amount": str(total_credit + total_debit),
        }

        filters_applied = credit_filter.get_applied_filters()
        if note_type:
            filters_applied["note_type"] = note_type

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
            set_cached(
                self.module, self.report_type, db_alias,
                cache_params, response_obj.data, self.cache_ttl,
            )

        return response_obj


# ═════════════════════════════════════════════════════════════
# Step 4 — Payment Reminder
# ═════════════════════════════════════════════════════════════

class PaymentReminderView(BaseReportView):
    """
    Payment Reminder — invoices with pending_amount > 0.
    ?view_type=summary  → grouped by customer (default)
    ?view_type=detail   → one row per invoice with days overdue
    """
    report_type = "payment_reminder"
    report_label = "Payment Reminder"
    module = "sales"
    filter_class = PaymentReminderFilter
    cache_ttl = 0  # real-time — no cache

    def get_queryset(self, request):
        return (
            SaleInvoiceOrders.objects
            .filter(is_deleted=False, pending_amount__gt=0)
            .select_related(
                "customer_id",
                "customer_address_id__city_id",
                "order_status_id",
            )
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_invoices=Count("sale_invoice_id"),
            total_billed=Coalesce(Sum("total_amount"), ZERO),
            total_paid=Coalesce(Sum("paid_amount"), ZERO),
            total_pending=Coalesce(Sum("pending_amount"), ZERO),
        )

    def get(self, request, *args, **kwargs):
        self._view_type = request.query_params.get("view_type", "summary").strip().lower()
        return self._handle_report(request)

    def serialize(self, queryset):
        import datetime
        today = datetime.date.today()

        if self._view_type == "detail":
            rows = []
            for inv in queryset:
                days_overdue = None
                if inv.due_date:
                    delta = (today - inv.due_date).days
                    days_overdue = delta if delta > 0 else 0
                rows.append({
                    "sale_invoice_id": str(inv.sale_invoice_id),
                    "invoice_no": inv.invoice_no,
                    "invoice_date": inv.invoice_date,
                    "due_date": inv.due_date,
                    "customer_name": inv.customer_id.name if inv.customer_id else None,
                    "total_amount": inv.total_amount,
                    "paid_amount": inv.paid_amount,
                    "pending_amount": inv.pending_amount,
                    "days_overdue": days_overdue,
                    "status": inv.order_status_id.status_name if inv.order_status_id else None,
                })
            return rows

        # Summary: group by customer
        customer_map = {}
        for inv in queryset:
            cid = str(inv.customer_id_id)
            cname = inv.customer_id.name if inv.customer_id else "Unknown"
            if cid not in customer_map:
                customer_map[cid] = {
                    "customer_id": cid,
                    "customer_name": cname,
                    "total_invoices": 0,
                    "total_billed": Decimal("0.00"),
                    "total_paid": Decimal("0.00"),
                    "total_pending": Decimal("0.00"),
                    "oldest_due_date": None,
                }
            row = customer_map[cid]
            row["total_invoices"] += 1
            row["total_billed"] += inv.total_amount or Decimal("0.00")
            row["total_paid"] += inv.paid_amount or Decimal("0.00")
            row["total_pending"] += inv.pending_amount or Decimal("0.00")
            if inv.due_date:
                if row["oldest_due_date"] is None or inv.due_date < row["oldest_due_date"]:
                    row["oldest_due_date"] = inv.due_date

        return sorted(
            customer_map.values(),
            key=lambda r: r["oldest_due_date"] or datetime.date.max
        )

    def _handle_report(self, request):
        from rest_framework.response import Response

        params = dict(request.query_params)
        flat_params = {
            k: v[0] if isinstance(v, list) and len(v) == 1 else v
            for k, v in params.items()
        }
        page, limit = get_page_and_limit(request)
        db_alias = self._get_db_alias(request)

        queryset = self.get_queryset(request)
        if db_alias:
            queryset = queryset.using(db_alias)

        report_filter = self.filter_class(flat_params)
        queryset = report_filter.apply(queryset)
        filters_applied = report_filter.get_applied_filters()
        filters_applied["view_type"] = self._view_type

        summary = self.get_summary(queryset)
        all_data = self.serialize(queryset)
        data, total = paginate_list(all_data, page, limit)

        return build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )


# ═════════════════════════════════════════════════════════════
# Step 4 — Customer Aging (Outstanding)
# ═════════════════════════════════════════════════════════════

class CustomerAgingView(BaseReportView):
    """
    Customer Aging — outstanding invoices bucketed by days overdue.
    Buckets: current (not due), 1-30, 31-60, 61-90, 91-120, 120+
    Optional: ?as_of_date=YYYY-MM-DD  (defaults to today)
    """
    report_type = "customer_aging"
    report_label = "Customer Aging (Outstanding)"
    module = "sales"
    cache_ttl = 900  # 15 min — heavy aggregate

    def get_queryset(self, request):
        return (
            SaleInvoiceOrders.objects
            .filter(is_deleted=False, pending_amount__gt=0)
            .select_related("customer_id")
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_customers=Count("customer_id", distinct=True),
            total_outstanding=Coalesce(Sum("pending_amount"), ZERO),
        )

    def get(self, request, *args, **kwargs):
        return self._handle_report(request)

    def _handle_report(self, request):
        import datetime
        from apps.reports.base.cache import get_cached, set_cached
        from rest_framework import status as drf_status
        from rest_framework.response import Response
        from apps.reports.base.filters import BaseReportFilter

        params = dict(request.query_params)
        flat_params = {
            k: v[0] if isinstance(v, list) and len(v) == 1 else v
            for k, v in params.items()
        }
        page, limit = get_page_and_limit(request)
        db_alias = self._get_db_alias(request)

        as_of_date_str = flat_params.get("as_of_date", "")
        as_of_date = BaseReportFilter._parse_date(as_of_date_str) or datetime.date.today()

        cache_params = {**flat_params, "_page": page, "_limit": limit}
        if self.cache_ttl > 0:
            cached = get_cached(self.module, self.report_type, db_alias, cache_params)
            if cached is not None:
                return Response(cached, status=drf_status.HTTP_200_OK)

        queryset = self.get_queryset(request)
        if db_alias:
            queryset = queryset.using(db_alias)

        report_filter = CustomerAgingFilter(flat_params)
        queryset = report_filter.apply(queryset)
        filters_applied = report_filter.get_applied_filters()
        filters_applied["as_of_date"] = str(as_of_date)

        summary = self.get_summary(queryset)

        # Build aging buckets in Python
        customer_map = {}
        for inv in queryset:
            cid = str(inv.customer_id_id)
            cname = inv.customer_id.name if inv.customer_id else "Unknown"
            pending = inv.pending_amount or Decimal("0.00")

            if cid not in customer_map:
                customer_map[cid] = {
                    "customer_id": cid,
                    "customer_name": cname,
                    "total_outstanding": Decimal("0.00"),
                    "current": Decimal("0.00"),
                    "days_1_30": Decimal("0.00"),
                    "days_31_60": Decimal("0.00"),
                    "days_61_90": Decimal("0.00"),
                    "days_91_120": Decimal("0.00"),
                    "days_120_plus": Decimal("0.00"),
                }

            row = customer_map[cid]
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

        rows = sorted(
            customer_map.values(),
            key=lambda r: r["total_outstanding"],
            reverse=True,
        )

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
            set_cached(
                self.module, self.report_type, db_alias,
                cache_params, response_obj.data, self.cache_ttl,
            )

        return response_obj


# ─────────────────────────────────────────────────────────────
# Step 5 — MIS Reports + Sales Order Analysis
# ─────────────────────────────────────────────────────────────

class NewCustomersView(BaseReportView):
    report_type = "mis_new_customers"
    report_label = "MIS — New Customers"
    module = "sales"
    cache_ttl = 600

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        from django.db.models import Min

        db_alias = getattr(request, "db_alias", "default")
        params = request.query_params
        cache_params = dict(params)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        page, limit = get_page_and_limit(request)
        f = NewCustomersFilter(params)

        base_qs = SaleInvoiceOrders.objects.using(db_alias).filter(
            is_deleted=False
        ).select_related("customer_id")

        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        first_invoice_qs = (
            SaleInvoiceOrders.objects.using(db_alias)
            .filter(is_deleted=False)
            .values("customer_id")
            .annotate(first_invoice_date=Min("invoice_date"))
        )
        first_invoice_map = {
            row["customer_id"]: row["first_invoice_date"]
            for row in first_invoice_qs
        }

        customer_ids = list(base_qs.values_list("customer_id", flat=True).distinct())
        date_from = f._applied.get("date_from")
        date_to = f._applied.get("date_to")

        new_customer_ids = []
        for cid in customer_ids:
            first_date = first_invoice_map.get(cid)
            if first_date is None:
                continue
            if date_from and first_date < date_from:
                continue
            if date_to and first_date > date_to:
                continue
            new_customer_ids.append(cid)

        if new_customer_ids:
            agg_qs = (
                SaleInvoiceOrders.objects.using(db_alias)
                .filter(is_deleted=False, customer_id__in=new_customer_ids)
                .values("customer_id", "customer_id__name", "customer_id__code")
                .annotate(
                    first_invoice_date=Min("invoice_date"),
                    total_invoices=Count("sale_invoice_id"),
                    total_sales_value=Coalesce(Sum("total_amount"), ZERO),
                )
                .order_by("first_invoice_date")
            )
            rows = [
                {
                    "customer_id": str(row["customer_id"]),
                    "customer_name": row["customer_id__name"] or "",
                    "customer_code": row["customer_id__code"],
                    "first_invoice_date": row["first_invoice_date"],
                    "total_invoices": row["total_invoices"],
                    "total_sales_value": row["total_sales_value"],
                }
                for row in agg_qs
            ]
        else:
            rows = []

        summary = {
            "total_new_customers": len(rows),
            "total_sales_value": str(sum(r["total_sales_value"] for r in rows)),
        }

        data, total = paginate_list(rows, page, limit)
        serializer = NewCustomerSerializer(data, many=True)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=serializer.data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )

        if self.cache_ttl > 0:
            set_cached(
                self.module, self.report_type, db_alias,
                cache_params, response_obj.data, self.cache_ttl,
            )

        return response_obj


class NoSalesCustomersView(BaseReportView):
    report_type = "mis_no_sales_customers"
    report_label = "MIS — No Sales Customers"
    module = "sales"
    cache_ttl = 600

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        from datetime import date as date_type
        from apps.reports.base.filters import BaseReportFilter

        db_alias = getattr(request, "db_alias", "default")
        params = request.query_params
        cache_params = dict(params)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        page, limit = get_page_and_limit(request)
        filters_applied = {}

        tmp = BaseReportFilter(params)
        from_date = tmp._parse_date(params.get("from_date"))
        to_date = tmp._parse_date(params.get("to_date"))
        if from_date:
            filters_applied["from_date"] = str(from_date)
        if to_date:
            filters_applied["to_date"] = str(to_date)

        inv_qs = SaleInvoiceOrders.objects.using(db_alias).filter(is_deleted=False)
        if from_date:
            inv_qs = inv_qs.filter(invoice_date__gte=from_date)
        if to_date:
            inv_qs = inv_qs.filter(invoice_date__lte=to_date)
        active_customer_ids = set(
            str(x) for x in inv_qs.values_list("customer_id", flat=True).distinct()
        )

        all_customers = Customer.objects.using(db_alias).filter(is_deleted=False)

        search = params.get("search", "").strip()
        if search:
            all_customers = all_customers.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
            filters_applied["search"] = search

        city = params.get("city", "").strip()
        if city:
            filters_applied["city"] = city

        from django.db.models import Max
        last_inv_map = {
            str(row["customer_id"]): row["last_date"]
            for row in SaleInvoiceOrders.objects.using(db_alias)
            .filter(is_deleted=False)
            .values("customer_id")
            .annotate(last_date=Max("invoice_date"))
        }

        today = date_type.today()
        rows = []
        for cust in all_customers.order_by("name"):
            if str(cust.customer_id) in active_customer_ids:
                continue
            last_date = last_inv_map.get(str(cust.customer_id))
            days_since = (today - last_date).days if last_date else None
            rows.append({
                "customer_id": str(cust.customer_id),
                "customer_name": cust.name or "",
                "customer_code": getattr(cust, "code", None),
                "last_invoice_date": last_date,
                "days_since_last_sale": days_since,
            })

        summary = {"total_no_sales_customers": len(rows)}

        data, total = paginate_list(rows, page, limit)
        serializer = NoSalesCustomerSerializer(data, many=True)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=serializer.data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )

        if self.cache_ttl > 0:
            set_cached(
                self.module, self.report_type, db_alias,
                cache_params, response_obj.data, self.cache_ttl,
            )

        return response_obj


class LimitExceededCustomersView(BaseReportView):
    report_type = "mis_limit_exceeded"
    report_label = "MIS — Credit Limit Exceeded Customers"
    module = "sales"
    cache_ttl = 600

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached

        db_alias = getattr(request, "db_alias", "default")
        params = request.query_params
        cache_params = dict(params)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        page, limit = get_page_and_limit(request)
        filters_applied = {}
        search = params.get("search", "").strip()

        outstanding_qs = (
            SaleInvoiceOrders.objects.using(db_alias)
            .filter(is_deleted=False, pending_amount__gt=0)
            .values("customer_id")
            .annotate(total_outstanding=Coalesce(Sum("pending_amount"), ZERO))
        )
        outstanding_map = {
            row["customer_id"]: row["total_outstanding"]
            for row in outstanding_qs
        }

        customers_qs = Customer.objects.using(db_alias).filter(
            is_deleted=False,
            credit_limit__isnull=False,
            credit_limit__gt=0,
        )
        if search:
            customers_qs = customers_qs.filter(
                Q(name__icontains=search) | Q(code__icontains=search)
            )
            filters_applied["search"] = search

        rows = []
        for cust in customers_qs.order_by("name"):
            outstanding = outstanding_map.get(cust.customer_id, Decimal("0.00"))
            credit_limit = cust.credit_limit or Decimal("0.00")
            if outstanding <= credit_limit:
                continue
            exceeded_by = outstanding - credit_limit
            rows.append({
                "customer_id": str(cust.customer_id),
                "customer_name": cust.name or "",
                "customer_code": getattr(cust, "code", None),
                "credit_limit": credit_limit,
                "total_outstanding": outstanding,
                "exceeded_by": exceeded_by,
            })

        rows.sort(key=lambda r: r["exceeded_by"], reverse=True)

        summary = {
            "total_customers_exceeded": len(rows),
            "total_exceeded_amount": str(sum(r["exceeded_by"] for r in rows)),
        }

        data, total = paginate_list(rows, page, limit)
        serializer = LimitExceededCustomerSerializer(data, many=True)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=serializer.data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )

        if self.cache_ttl > 0:
            set_cached(
                self.module, self.report_type, db_alias,
                cache_params, response_obj.data, self.cache_ttl,
            )

        return response_obj


class SalesOrderAnalysisView(BaseReportView):
    report_type = "sales_order_analysis"
    report_label = "Sales Order Analysis"
    module = "sales"
    cache_ttl = 600

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached

        db_alias = getattr(request, "db_alias", "default")
        params = request.query_params
        cache_params = dict(params)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        page, limit = get_page_and_limit(request)
        f = SalesOrderAnalysisFilter(params)

        base_qs = SaleOrder.objects.using(db_alias).filter(
            is_deleted=False
        ).select_related(
            "customer_id",
            "order_status_id",
            "flow_status_id",
            "sale_type_id",
        )

        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        summary_agg = base_qs.aggregate(
            total_orders=Count("sale_order_id"),
            total_value=Coalesce(Sum("total_amount"), ZERO),
        )

        agg_qs = (
            base_qs
            .values("customer_id", "customer_id__name")
            .annotate(
                total_orders=Count("sale_order_id"),
                completed_orders=Count(
                    "sale_order_id",
                    filter=Q(order_status_id__status_name__iexact="completed"),
                ),
                total_value=Coalesce(Sum("total_amount"), ZERO),
            )
            .order_by("-total_value")
        )

        rows = []
        for row in agg_qs:
            total_orders = row["total_orders"] or 0
            completed = row["completed_orders"] or 0
            total_val = row["total_value"] or Decimal("0.00")
            avg_val = (total_val / total_orders) if total_orders else Decimal("0.00")
            rows.append({
                "customer_id": str(row["customer_id"]),
                "customer_name": row["customer_id__name"] or "",
                "total_orders": total_orders,
                "completed_orders": completed,
                "pending_orders": total_orders - completed,
                "total_value": total_val,
                "avg_order_value": avg_val,
            })

        summary = {
            "total_customers": len(rows),
            "total_orders": summary_agg["total_orders"] or 0,
            "total_value": str(summary_agg["total_value"]),
        }

        data, total = paginate_list(rows, page, limit)
        serializer = SalesOrderAnalysisSerializer(data, many=True)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=serializer.data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )

        if self.cache_ttl > 0:
            set_cached(
                self.module, self.report_type, db_alias,
                cache_params, response_obj.data, self.cache_ttl,
            )

        return response_obj


# ─────────────────────────────────────────────────────────────
# Step 6 - Analysis Reports (beats MaxxERP)
# ─────────────────────────────────────────────────────────────

class ProductSalesAnalysisView(BaseReportView):
    # GET /api/v1/reports/sales/analysis/product/
    report_type = "analysis_product"
    report_label = "Product Sales Analysis"
    module = "sales"
    cache_ttl = 600

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        from apps.reports.sales.filters import SalesRegisterItemFilter

        db_alias = getattr(request, "db_alias", "default")
        params = request.query_params
        cache_params = dict(params)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        page, limit = get_page_and_limit(request)
        f = SalesRegisterItemFilter(params)

        base_qs = SaleInvoiceItems.objects.using(db_alias).filter(
            sale_invoice_id__is_deleted=False
        ).select_related("product_id", "sale_invoice_id")

        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        summary_agg = base_qs.aggregate(
            total_qty=Coalesce(Sum("quantity"), ZERO),
            total_revenue=Coalesce(Sum("amount"), ZERO),
            total_discount=Coalesce(Sum("discount"), ZERO),
        )

        agg_qs = (
            base_qs
            .values("product_id", "product_id__name", "product_id__code")
            .annotate(
                total_qty=Coalesce(Sum("quantity"), ZERO),
                gross_amount=Coalesce(Sum("amount"), ZERO),
                total_discount=Coalesce(Sum("discount"), ZERO),
                cgst_sum=Coalesce(Sum("cgst"), ZERO),
                sgst_sum=Coalesce(Sum("sgst"), ZERO),
                igst_sum=Coalesce(Sum("igst"), ZERO),
                invoice_count=Count("sale_invoice_id", distinct=True),
            )
            .order_by("-gross_amount")
        )

        rows = []
        for row in agg_qs:
            cgst = row["cgst_sum"] or Decimal("0.00")
            sgst = row["sgst_sum"] or Decimal("0.00")
            igst = row["igst_sum"] or Decimal("0.00")
            total_tax = cgst + sgst + igst
            gross = row["gross_amount"] or Decimal("0.00")
            qty = row["total_qty"] or Decimal("0.00")
            avg_rate = (gross / qty) if qty else Decimal("0.00")
            rows.append({
                "product_id": str(row["product_id"]),
                "product_name": row["product_id__name"] or "",
                "product_code": row["product_id__code"],
                "total_qty": qty,
                "gross_amount": gross,
                "total_discount": row["total_discount"] or Decimal("0.00"),
                "total_tax": total_tax,
                "net_amount": gross + total_tax,
                "avg_rate": avg_rate,
            })

        summary = {
            "total_products": len(rows),
            "total_qty": str(summary_agg["total_qty"]),
            "total_revenue": str(summary_agg["total_revenue"]),
            "total_discount": str(summary_agg["total_discount"]),
        }

        data, total = paginate_list(rows, page, limit)
        serializer = ProductSalesAnalysisSerializer(data, many=True)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=serializer.data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )

        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, response_obj.data, self.cache_ttl)

        return response_obj


class CustomerSalesAnalysisView(BaseReportView):
    # GET /api/v1/reports/sales/analysis/customer/
    report_type = "analysis_customer"
    report_label = "Customer Sales Analysis"
    module = "sales"
    cache_ttl = 600

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        from apps.reports.sales.filters import SalesRegisterFilter
        from django.db.models import Max

        db_alias = getattr(request, "db_alias", "default")
        params = request.query_params
        cache_params = dict(params)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        page, limit = get_page_and_limit(request)
        f = SalesRegisterFilter(params)

        base_qs = SaleInvoiceOrders.objects.using(db_alias).filter(
            is_deleted=False
        ).select_related("customer_id", "customer_address_id__city_id")

        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        summary_agg = base_qs.aggregate(
            total_invoices=Count("sale_invoice_id"),
            total_amount=Coalesce(Sum("total_amount"), ZERO),
            total_paid=Coalesce(Sum("paid_amount"), ZERO),
            total_pending=Coalesce(Sum("pending_amount"), ZERO),
        )

        agg_qs = (
            base_qs
            .values("customer_id", "customer_id__name")
            .annotate(
                total_invoices=Count("sale_invoice_id"),
                total_amount=Coalesce(Sum("total_amount"), ZERO),
                total_paid=Coalesce(Sum("paid_amount"), ZERO),
                total_pending=Coalesce(Sum("pending_amount"), ZERO),
                last_invoice_date=Max("invoice_date"),
            )
            .order_by("-total_amount")
        )

        rows = []
        for row in agg_qs:
            inv_count = row["total_invoices"] or 0
            total = row["total_amount"] or Decimal("0.00")
            avg = (total / inv_count) if inv_count else Decimal("0.00")
            rows.append({
                "customer_id": str(row["customer_id"]),
                "customer_name": row["customer_id__name"] or "",
                "total_invoices": inv_count,
                "total_amount": total,
                "total_paid": row["total_paid"] or Decimal("0.00"),
                "total_pending": row["total_pending"] or Decimal("0.00"),
                "avg_invoice_value": avg,
                "last_invoice_date": row["last_invoice_date"],
            })

        summary = {
            "total_customers": len(rows),
            "total_invoices": summary_agg["total_invoices"] or 0,
            "total_amount": str(summary_agg["total_amount"]),
            "total_paid": str(summary_agg["total_paid"]),
            "total_pending": str(summary_agg["total_pending"]),
        }

        data, total = paginate_list(rows, page, limit)
        serializer = CustomerSalesAnalysisSerializer(data, many=True)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=serializer.data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )

        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, response_obj.data, self.cache_ttl)

        return response_obj


class SalespersonAnalysisView(BaseReportView):
    # GET /api/v1/reports/sales/analysis/salesperson/
    report_type = "analysis_salesperson"
    report_label = "Salesperson Performance Analysis"
    module = "sales"
    cache_ttl = 600

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        from apps.reports.sales.filters import SalesRegisterFilter

        db_alias = getattr(request, "db_alias", "default")
        params = request.query_params
        cache_params = dict(params)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        page, limit = get_page_and_limit(request)
        f = SalesRegisterFilter(params)

        base_qs = SaleInvoiceOrders.objects.using(db_alias).filter(
            is_deleted=False,
            order_salesman_id__isnull=False,
        ).select_related("order_salesman_id")

        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        agg_qs = (
            base_qs
            .values("order_salesman_id", "order_salesman_id__name")
            .annotate(
                total_invoices=Count("sale_invoice_id"),
                total_sales=Coalesce(Sum("total_amount"), ZERO),
                total_collected=Coalesce(Sum("paid_amount"), ZERO),
                total_pending=Coalesce(Sum("pending_amount"), ZERO),
            )
            .order_by("-total_sales")
        )

        rows = []
        for row in agg_qs:
            total_sales = row["total_sales"] or Decimal("0.00")
            collected = row["total_collected"] or Decimal("0.00")
            collection_pct = (collected / total_sales * 100).quantize(Decimal("0.01")) if total_sales else Decimal("0.00")
            rows.append({
                "salesperson_id": str(row["order_salesman_id"]),
                "salesperson_name": row["order_salesman_id__name"] or "",
                "total_invoices": row["total_invoices"] or 0,
                "total_sales": total_sales,
                "total_collected": collected,
                "total_pending": row["total_pending"] or Decimal("0.00"),
                "collection_pct": collection_pct,
            })

        summary = {
            "total_salespersons": len(rows),
            "total_sales": str(sum(r["total_sales"] for r in rows)),
            "total_collected": str(sum(r["total_collected"] for r in rows)),
        }

        data, total = paginate_list(rows, page, limit)
        serializer = SalespersonAnalysisSerializer(data, many=True)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=serializer.data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )

        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, response_obj.data, self.cache_ttl)

        return response_obj


class ProfitMarginView(BaseReportView):
    # GET /api/v1/reports/sales/profit-margin/
    # Uses SaleInvoiceItems + Products.purchase_rate for cost
    report_type = "profit_margin"
    report_label = "Profit Margin Analysis"
    module = "sales"
    cache_ttl = 900

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        from apps.reports.sales.filters import SalesRegisterItemFilter
        from apps.ai_features.services.profit_margin_service import get_product_cost_map

        db_alias = getattr(request, "db_alias", "default")
        params = request.query_params
        cache_params = dict(params)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        page, limit = get_page_and_limit(request)
        f = SalesRegisterItemFilter(params)

        # ALL sold items (not only catalog-priced ones). Cost is resolved per
        # product via the SHARED resolver — same logic as the Profit Margin
        # insight — so the two never disagree (CLAUDE.md §4B / flow.md).
        base_qs = SaleInvoiceItems.objects.using(db_alias).filter(
            sale_invoice_id__is_deleted=False,
        ).select_related("product_id", "sale_invoice_id")

        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        agg_qs = (
            base_qs
            .values(
                "product_id",
                "product_id__name",
                "product_id__code",
                "product_id__purchase_rate",
            )
            .annotate(
                total_qty=Coalesce(Sum("quantity"), ZERO),
                total_revenue=Coalesce(Sum("amount"), ZERO),
            )
            .order_by("-total_revenue")
        )
        agg_list = list(agg_qs)
        product_ids = [r["product_id"] for r in agg_list]

        # Unit cost from the SHARED cost map (all-time weighted-average purchase
        # cost → catalog → unknown) — identical to the Profit Margin insight.
        cost_map = get_product_cost_map(product_ids, db_alias)

        rows = []
        for row in agg_list:
            pid = str(row["product_id"])
            qty = row["total_qty"] or Decimal("0.00")
            revenue = row["total_revenue"] or Decimal("0.00")
            cost_per_unit, cost_source = cost_map.get(pid, (None, "unknown"))
            if cost_per_unit is None:
                # Honest empty state — cost not set, profit/margin unknowable.
                cost = None
                profit = None
                margin_pct = None
            else:
                cost = (Decimal(str(cost_per_unit)) * qty).quantize(Decimal("0.01"))
                profit = revenue - cost
                margin_pct = (profit / revenue * 100).quantize(Decimal("0.01")) if revenue else Decimal("0.00")
            rows.append({
                "product_id": str(row["product_id"]),
                "product_name": row["product_id__name"] or "",
                "product_code": row["product_id__code"],
                "total_qty": qty,
                "total_revenue": revenue,
                "total_cost": cost,
                "gross_profit": profit,
                "margin_pct": margin_pct,
                "cost_source": cost_source,
            })

        # Totals from rows with a KNOWN cost only — never fabricate cost/profit.
        known = [r for r in rows if r["total_cost"] is not None]
        summary = {
            "total_products": len(rows),
            "no_cost_count": len(rows) - len(known),
            "total_revenue": str(sum(r["total_revenue"] for r in rows)),
            "total_cost": str(sum(r["total_cost"] for r in known)),
            "total_profit": str(sum(r["gross_profit"] for r in known)),
        }

        data, total = paginate_list(rows, page, limit)
        serializer = ProfitMarginSerializer(data, many=True)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=serializer.data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )

        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, response_obj.data, self.cache_ttl)

        return response_obj


class SalesTrendView(BaseReportView):
    # GET /api/v1/reports/sales/sales-trend/
    # Params: compare_type=monthly|quarterly, current_year=YYYY, previous_year=YYYY
    report_type = "sales_trend"
    report_label = "Sales Trend (YoY)"
    module = "sales"
    cache_ttl = 900

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        from django.db.models.functions import ExtractMonth, ExtractQuarter
        from datetime import date

        db_alias = getattr(request, "db_alias", "default")
        params = request.query_params
        cache_params = dict(params)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        page, limit = get_page_and_limit(request)

        compare_type = params.get("compare_type", "monthly").lower()
        if compare_type not in ("monthly", "quarterly"):
            compare_type = "monthly"

        this_year = date.today().year
        try:
            current_year = int(params.get("current_year", this_year))
        except (ValueError, TypeError):
            current_year = this_year
        try:
            previous_year = int(params.get("previous_year", current_year - 1))
        except (ValueError, TypeError):
            previous_year = current_year - 1

        filters_applied = {
            "compare_type": compare_type,
            "current_year": current_year,
            "previous_year": previous_year,
        }

        base_qs = SaleInvoiceOrders.objects.using(db_alias).filter(is_deleted=False)

        def fetch_year_data(year):
            qs = base_qs.filter(invoice_date__year=year)
            if compare_type == "monthly":
                return {
                    row["period_num"]: row["sales"]
                    for row in qs.annotate(period_num=ExtractMonth("invoice_date"))
                    .values("period_num")
                    .annotate(sales=Coalesce(Sum("total_amount"), ZERO))
                }
            return {
                row["period_num"]: row["sales"]
                for row in qs.annotate(period_num=ExtractQuarter("invoice_date"))
                .values("period_num")
                .annotate(sales=Coalesce(Sum("total_amount"), ZERO))
            }

        current_data = fetch_year_data(current_year)
        previous_data = fetch_year_data(previous_year)

        periods = range(1, 13) if compare_type == "monthly" else range(1, 5)

        def period_label(n):
            if compare_type == "monthly":
                return "{}-{}".format(current_year, str(n).zfill(2))
            return "{}-Q{}".format(current_year, n)

        rows = []
        for p in periods:
            curr = current_data.get(p, Decimal("0.00"))
            prev = previous_data.get(p, Decimal("0.00"))
            growth = curr - prev
            growth_pct = (growth / prev * 100).quantize(Decimal("0.01")) if prev else Decimal("0.00")
            rows.append({
                "period": period_label(p),
                "current_year_sales": curr,
                "previous_year_sales": prev,
                "growth_amount": growth,
                "growth_pct": growth_pct,
            })

        summary = {
            "current_year": current_year,
            "previous_year": previous_year,
            "current_year_total": str(sum(r["current_year_sales"] for r in rows)),
            "previous_year_total": str(sum(r["previous_year_sales"] for r in rows)),
        }

        data, total = paginate_list(rows, page, limit)
        serializer = SalesTrendSerializer(data, many=True)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=serializer.data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )

        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, response_obj.data, self.cache_ttl)

        return response_obj


class GstSummaryView(BaseReportView):
    # GET /api/v1/reports/sales/tax/gst-summary/
    report_type = "gst_summary"
    report_label = "GST Summary"
    module = "sales"
    cache_ttl = 900

    def get(self, request, *args, **kwargs):
        from apps.reports.base.cache import get_cached, set_cached
        from apps.reports.sales.filters import SalesRegisterItemFilter

        db_alias = getattr(request, "db_alias", "default")
        params = request.query_params
        cache_params = dict(params)

        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        if cached is not None:
            return Response(cached)

        page, limit = get_page_and_limit(request)
        f = SalesRegisterItemFilter(params)

        base_qs = SaleInvoiceItems.objects.using(db_alias).filter(
            sale_invoice_id__is_deleted=False
        ).select_related("sale_invoice_id", "sale_invoice_id__customer_id")

        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        agg_qs = (
            base_qs
            .values(
                "sale_invoice_id",
                "sale_invoice_id__invoice_no",
                "sale_invoice_id__invoice_date",
                "sale_invoice_id__customer_id__name",
            )
            .annotate(
                taxable_amount=Coalesce(Sum("amount"), ZERO),
                cgst=Coalesce(Sum("cgst"), ZERO),
                sgst=Coalesce(Sum("sgst"), ZERO),
                igst=Coalesce(Sum("igst"), ZERO),
            )
            .order_by("sale_invoice_id__invoice_date")
        )

        rows = []
        for row in agg_qs:
            cgst = row["cgst"] or Decimal("0.00")
            sgst = row["sgst"] or Decimal("0.00")
            igst = row["igst"] or Decimal("0.00")
            total_tax = cgst + sgst + igst
            taxable = row["taxable_amount"] or Decimal("0.00")
            rows.append({
                "invoice_no": row["sale_invoice_id__invoice_no"] or "",
                "invoice_date": row["sale_invoice_id__invoice_date"],
                "customer_name": row["sale_invoice_id__customer_id__name"] or "",
                "taxable_amount": taxable,
                "cgst": cgst,
                "sgst": sgst,
                "igst": igst,
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
        serializer = GstSummarySerializer(data, many=True)

        response_obj = build_report_response(
            report_type=self.report_type,
            report_label=self.report_label,
            data=serializer.data,
            summary=summary,
            filters_applied=filters_applied,
            page=page,
            limit=limit,
            total=total,
        )

        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params, response_obj.data, self.cache_ttl)

        return response_obj
