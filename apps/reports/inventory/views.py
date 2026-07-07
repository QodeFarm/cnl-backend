"""
Inventory reports — current-stock snapshots from the Products table.

Field reality (verified against apps/products/models.py):
  Products: name, code, hsn_code, status, balance (current stock qty),
      physical_balance, minimum_level, maximum_level, purchase_rate, sales_rate,
      mrp, product_group_id, category_id, brand_id, unit_options_id, is_deleted
  ProductItemBalance: product_id, warehouse_location_id, quantity
"""

import datetime
from decimal import Decimal

from django.db.models import Count, Sum, F, Value, DecimalField, IntegerField, ExpressionWrapper, Max, Case, When, Q
from django.db.models.functions import Coalesce

from rest_framework.response import Response

from apps.reports.base.views import BaseReportView
from apps.reports.base.pagination import get_page_and_limit, paginate_list
from apps.reports.base.response import build_report_response
from apps.reports.inventory.filters import InventoryProductFilter, StockMovementFilter
from apps.products.models import Products, ProductItemBalance
from apps.sales.models import SaleInvoiceItems, SaleOrderItems
from apps.production.models import StockJournal
from apps.reports.sales.filters import SalesRegisterItemFilter

ZERO = Value(Decimal("0.00"), output_field=DecimalField(max_digits=18, decimal_places=2))


def _product_base_qs():
    return (
        Products.objects
        .filter(is_deleted=False)
        .select_related("product_group_id", "category_id", "brand_id", "unit_options_id")
    )


def _common_fields(p):
    """Identity columns shared by the stock reports."""
    return {
        "product_id": str(p.product_id),
        "product_name": p.name,
        "product_code": p.code,
        "hsn_code": p.hsn_code,
        "product_group": p.product_group_id.group_name if p.product_group_id else None,
        "category": p.category_id.category_name if p.category_id else None,
        "brand": p.brand_id.brand_name if p.brand_id else None,
        "unit": p.unit_options_id.unit_name if p.unit_options_id else None,
    }


class StockSummaryView(BaseReportView):
    """Current stock per product with reorder levels and stock status."""
    report_type = "stock_summary"
    report_label = "Stock Summary"
    module = "inventory"
    filter_class = InventoryProductFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return _product_base_qs()

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_products=Count("product_id"),
            total_stock_qty=Coalesce(Sum("balance"), Value(0)),
        )

    def serialize(self, queryset):
        rows = []
        for p in queryset:
            balance = p.balance or 0
            min_level = p.minimum_level
            stock_status = "OK"
            if min_level is not None and min_level > 0 and balance <= min_level:
                stock_status = "Low" if balance > 0 else "Out of Stock"
            rows.append({
                **_common_fields(p),
                "balance": balance,
                "minimum_level": min_level,
                "maximum_level": p.maximum_level,
                "status": p.status,
                "stock_status": stock_status,
            })
        return rows


class StockValuationView(BaseReportView):
    """Stock value per product: qty x cost (purchase_rate) and qty x sale (sales_rate)."""
    report_type = "stock_valuation"
    report_label = "Stock Valuation"
    module = "inventory"
    filter_class = InventoryProductFilter
    cache_ttl = 600

    def get_queryset(self, request):
        return _product_base_qs()

    def get_summary(self, queryset):
        cost_expr = ExpressionWrapper(
            F("balance") * Coalesce(F("purchase_rate"), ZERO),
            output_field=DecimalField(max_digits=18, decimal_places=2),
        )
        sale_expr = ExpressionWrapper(
            F("balance") * Coalesce(F("sales_rate"), ZERO),
            output_field=DecimalField(max_digits=18, decimal_places=2),
        )
        agg = queryset.aggregate(
            total_products=Count("product_id"),
            # value is summed only over PRICED stock (Coalesce makes unpriced 0).
            priced_products=Count("product_id", filter=Q(purchase_rate__gt=0)),
            total_qty=Coalesce(Sum("balance"), Value(0)),
            total_cost_value=Coalesce(Sum(cost_expr), ZERO),
            total_sale_value=Coalesce(Sum(sale_expr), ZERO),
        )
        # Surface how many products have NO cost, so a ₹0 total is read as
        # "cost not set", not "worthless" (honest empty state — flow.md / §3).
        agg["unpriced_products"] = agg["total_products"] - agg["priced_products"]
        return agg

    def serialize(self, queryset):
        rows = []
        for p in queryset:
            balance = Decimal(p.balance or 0)
            pr = p.purchase_rate if (p.purchase_rate and p.purchase_rate > 0) else None
            sr = p.sales_rate if (p.sales_rate and p.sales_rate > 0) else None
            rows.append({
                **_common_fields(p),
                "balance": p.balance or 0,
                # null when not set — never a fake ₹0 value for unpriced stock.
                "purchase_rate": pr,
                "sales_rate": sr,
                "stock_cost_value": (balance * pr) if pr is not None else None,
                "stock_sale_value": (balance * sr) if sr is not None else None,
            })
        return rows


class ReorderLevelView(BaseReportView):
    """Items at or below their minimum level — what needs reordering."""
    report_type = "reorder_level"
    report_label = "Reorder Level (Replenishment)"
    module = "inventory"
    filter_class = InventoryProductFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            _product_base_qs()
            .filter(minimum_level__isnull=False, minimum_level__gt=0, balance__lte=F("minimum_level"))
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_items_to_reorder=Count("product_id"),
            total_current_qty=Coalesce(Sum("balance"), Value(0)),
        )

    def serialize(self, queryset):
        rows = []
        for p in queryset:
            balance = p.balance or 0
            min_level = p.minimum_level or 0
            max_level = p.maximum_level
            shortfall = max(min_level - balance, 0)
            reorder_qty = (max_level - balance) if (max_level and max_level > balance) else shortfall
            rows.append({
                **_common_fields(p),
                "balance": balance,
                "minimum_level": min_level,
                "maximum_level": max_level,
                "shortfall": shortfall,
                "reorder_qty": reorder_qty,
            })
        return rows


# =============================================================
# Iteration 2 - Godown-wise Stock + Fast Moving + Slow Moving
# =============================================================

class GodownStockView(BaseReportView):
    """Stock quantity per product per warehouse location (where stock exists)."""
    report_type = "godown_stock"
    report_label = "Godown-wise Stock"
    module = "inventory"
    filter_class = None
    cache_ttl = 300

    def get_queryset(self, request):
        qs = (
            ProductItemBalance.objects
            .filter(quantity__gt=0)
            .select_related("product_id", "warehouse_location_id", "warehouse_location_id__warehouse_id")
        )
        search = request.query_params.get("search", "").strip()
        if search:
            qs = qs.filter(product_id__name__icontains=search)
        return qs.order_by("warehouse_location_id__location_name", "product_id__name")

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_rows=Count("product_item_balance_id"),
            total_qty=Coalesce(Sum("quantity"), Value(0)),
        )

    def serialize(self, queryset):
        rows = []
        for b in queryset:
            loc = b.warehouse_location_id
            wh = loc.warehouse_id if loc else None
            rows.append({
                "product_item_balance_id": str(b.product_item_balance_id),
                "warehouse": wh.name if wh else None,
                "location": loc.location_name if loc else None,
                "product_name": b.product_id.name if b.product_id else None,
                "product_code": b.product_id.code if b.product_id else None,
                "quantity": b.quantity,
            })
        return rows


class _MovingBase(BaseReportView):
    """Shared flatten + cache + Response plumbing for moving-stock reports."""
    cache_ttl = 600

    @staticmethod
    def _flat_params(request):
        params = dict(request.query_params)
        return {k: v[0] if isinstance(v, list) and len(v) == 1 else v for k, v in params.items()}

    def _cached(self, request, cache_params):
        from apps.reports.base.cache import get_cached
        db_alias = self._get_db_alias(request) or "default"
        cached = get_cached(self.module, self.report_type, db_alias, cache_params)
        return Response(cached) if cached is not None else None

    def _store(self, request, cache_params, payload):
        from apps.reports.base.cache import set_cached
        if self.cache_ttl > 0:
            db_alias = self._get_db_alias(request) or "default"
            set_cached(self.module, self.report_type, db_alias, cache_params, payload, self.cache_ttl)


class FastMovingView(_MovingBase):
    """Top-selling products by quantity sold in the period (from sale invoices)."""
    report_type = "fast_moving"
    report_label = "Fast Moving Items"
    module = "inventory"

    def get(self, request, *args, **kwargs):
        flat = self._flat_params(request)
        page, limit = get_page_and_limit(request)
        cache_params = {**flat, "_page": page, "_limit": limit}
        hit = self._cached(request, cache_params)
        if hit is not None:
            return hit

        db_alias = self._get_db_alias(request) or "default"
        f = SalesRegisterItemFilter(flat)
        base_qs = (
            SaleInvoiceItems.objects.using(db_alias)
            .filter(sale_invoice_id__is_deleted=False)
            .select_related("product_id", "sale_invoice_id")
        )
        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        agg = (
            base_qs
            .values("product_id", "product_id__name", "product_id__code")
            .annotate(
                total_qty_sold=Coalesce(Sum("quantity"), ZERO),
                total_revenue=Coalesce(Sum("amount"), ZERO),
                invoice_count=Count("sale_invoice_id", distinct=True),
            )
            .order_by("-total_qty_sold")
        )
        rows = [{
            "product_id": str(r["product_id"]),
            "product_name": r["product_id__name"] or "",
            "product_code": r["product_id__code"],
            "total_qty_sold": r["total_qty_sold"],
            "total_revenue": r["total_revenue"],
            "invoice_count": r["invoice_count"],
        } for r in agg]

        summary = {
            "total_products": len(rows),
            "total_qty_sold": str(sum((r["total_qty_sold"] for r in rows), Decimal("0.00"))),
            "total_revenue": str(sum((r["total_revenue"] for r in rows), Decimal("0.00"))),
        }
        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        self._store(request, cache_params, resp.data)
        return resp


class SlowMovingView(_MovingBase):
    """In-stock products NOT sold within the selected period (slow / dead stock)."""
    report_type = "slow_moving"
    report_label = "Slow Moving Items"
    module = "inventory"

    def get(self, request, *args, **kwargs):
        flat = self._flat_params(request)
        page, limit = get_page_and_limit(request)
        cache_params = {**flat, "_page": page, "_limit": limit}
        hit = self._cached(request, cache_params)
        if hit is not None:
            return hit

        db_alias = self._get_db_alias(request) or "default"

        # product_ids sold within the selected period (date filter via the sales item filter)
        f = SalesRegisterItemFilter(flat)
        sold_qs = SaleInvoiceItems.objects.using(db_alias).filter(sale_invoice_id__is_deleted=False)
        sold_qs = f.apply(sold_qs)
        filters_applied = f.get_applied_filters()
        sold_ids = set(str(x) for x in sold_qs.values_list("product_id", flat=True).distinct())

        # last-ever sold date per product (to show how long it has been idle)
        last_sold = {
            str(r["product_id"]): r["last_date"]
            for r in SaleInvoiceItems.objects.using(db_alias)
            .filter(sale_invoice_id__is_deleted=False)
            .values("product_id")
            .annotate(last_date=Max("sale_invoice_id__invoice_date"))
        }

        prod_qs = (
            Products.objects.using(db_alias)
            .filter(is_deleted=False, balance__gt=0)
            .select_related("product_group_id")
            .order_by("name")
        )
        search = flat.get("search", "").strip()
        if search:
            prod_qs = prod_qs.filter(name__icontains=search)

        today = datetime.date.today()
        rows = []
        for p in prod_qs:
            pid = str(p.product_id)
            if pid in sold_ids:
                continue
            ld = last_sold.get(pid)
            rows.append({
                "product_id": pid,
                "product_name": p.name,
                "product_code": p.code,
                "product_group": p.product_group_id.group_name if p.product_group_id else None,
                "balance": p.balance or 0,
                "last_sold_date": ld,
                "days_since_sold": (today - ld).days if ld else None,
            })

        summary = {
            "total_slow_items": len(rows),
            "total_stock_qty": sum(r["balance"] for r in rows),
        }
        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        self._store(request, cache_params, resp.data)
        return resp


# =============================================================
# Stock Movement Report - from the StockJournal ledger (Receive / Issue)
# =============================================================

class StockMovementView(BaseReportView):
    """All stock-in (Receive) and stock-out (Issue) ledger entries per product."""
    report_type = "stock_movement"
    report_label = "Stock Movement"
    module = "inventory"
    filter_class = StockMovementFilter
    cache_ttl = 0  # transactional ledger - keep real-time

    def get_queryset(self, request):
        return (
            StockJournal.objects
            .filter(is_deleted=False)
            .select_related("product_id")
        )

    def get_summary(self, queryset):
        agg = queryset.aggregate(
            total_movements=Count("journal_id"),
            total_received=Coalesce(
                Sum(Case(
                    When(transaction_type__iexact="Receive", then="quantity"),
                    default=Value(0),
                    output_field=DecimalField(max_digits=18, decimal_places=3),
                )), ZERO,
            ),
            total_issued=Coalesce(
                Sum(Case(
                    When(transaction_type__iexact="Issue", then="quantity"),
                    default=Value(0),
                    output_field=DecimalField(max_digits=18, decimal_places=3),
                )), ZERO,
            ),
        )
        agg["net_movement"] = (agg["total_received"] or Decimal("0")) - (agg["total_issued"] or Decimal("0"))
        return agg

    def serialize(self, queryset):
        rows = []
        for j in queryset:
            rows.append({
                "journal_id": str(j.journal_id),
                "date": j.created_at,
                "product_name": j.product_id.name if j.product_id else None,
                "product_code": j.product_id.code if j.product_id else None,
                "transaction_type": j.transaction_type,
                "quantity": j.quantity,
                "reference_id": j.reference_id,
                "remarks": j.remarks,
            })
        return rows


# =============================================================
# Stock Forecast - current stock vs average sales demand (RED/YELLOW/GREEN)
# Same forecast logic as the legacy inventory/stock_forecast_report endpoint,
# rebuilt in the reports framework so it speaks the hub's conventions
# (period param + standard response) and the Quick Period filter works.
# =============================================================

class StockForecastView(_MovingBase):
    report_type = "stock_forecast"
    report_label = "Stock Forecast"
    module = "inventory"
    cache_ttl = 600

    # Quick Period -> sales window in days. Keys match TaTable's quickPeriodOptions
    # (today, yesterday, last_week, current_month, last_month, last_six_months,
    #  current_quarter, year_to_date, last_year). Default 6 months, as the legacy view.
    PERIOD_DAYS = {
        "today": 1, "yesterday": 1, "last_week": 7,
        "current_month": 30, "last_month": 30,
        "last_six_months": 180, "current_quarter": 90,
        "year_to_date": 365, "last_year": 365,
    }

    def get(self, request, *args, **kwargs):
        flat = self._flat_params(request)
        page, limit = get_page_and_limit(request)
        cache_params = {**flat, "_page": page, "_limit": limit}
        hit = self._cached(request, cache_params)
        if hit is not None:
            return hit

        db_alias = self._get_db_alias(request) or "default"
        period_days = self.PERIOD_DAYS.get(flat.get("period", "").strip().lower(), 180)
        months = max(period_days / 30.0, 1)

        # Products: active only (exclude Inactive — don't forecast discontinued
        # items) so the report total matches the at-risk insight total. Apply only
        # the group/category/brand/status/search filters (NOT the date layer —
        # period drives the SALES window, not product creation).
        base = (
            Products.objects.using(db_alias)
            .filter(is_deleted=False)
            .exclude(status="Inactive")
            .select_related("product_group_id", "unit_options_id")
        )
        f = InventoryProductFilter(flat)
        base = f.apply_secondary_filters(base)
        filters_applied = f.get_applied_filters()
        filters_applied["period_days"] = period_days

        # Sales demand over the window (invoices + orders), keyed by product_id
        end = datetime.date.today()
        start = end - datetime.timedelta(days=period_days)
        sales = {}
        for it in (SaleInvoiceItems.objects.using(db_alias)
                   .filter(sale_invoice_id__invoice_date__gte=start, sale_invoice_id__invoice_date__lte=end)
                   .values("product_id").annotate(q=Coalesce(Sum("quantity"), ZERO))):
            sales[str(it["product_id"])] = Decimal(it["q"] or 0)
        for it in (SaleOrderItems.objects.using(db_alias)
                   .filter(sale_order_id__order_date__gte=start, sale_order_id__order_date__lte=end)
                   .values("product_id").annotate(q=Coalesce(Sum("quantity"), Value(0)))):
            pid = str(it["product_id"])
            sales[pid] = sales.get(pid, Decimal(0)) + Decimal(it["q"] or 0)

        from apps.ai_features.services.stock_forecast_service import forecast_status

        rank = {"RED": 0, "YELLOW": 1, "GREEN": 2}
        red = yellow = green = 0
        rows = []
        for p in base:
            total = float(sales.get(str(p.product_id), 0))
            # Forecast only products WITH demand (consistent with the insight) —
            # no-demand items belong in Low Stock / Dead Stock, not a sales
            # forecast, and must never read "healthy" while at 0 stock (flow.md).
            if total <= 0:
                continue
            current = float(p.balance or 0)
            avg = round(total / months, 2)
            diff = round(current - avg, 2)
            # Shared status — identical formula to the at-risk Stock Forecast insight.
            st, _days = forecast_status(current, avg)
            if st == "RED":
                red += 1
                msg = "Critical - No Stock" if current <= 0 else "Critical - Stock Below Average Sales"
            elif st == "YELLOW":
                yellow += 1
                msg = "Warning - Stock Cover Below 2 Months"
            else:
                green += 1
                msg = "No Demand Data - Monitor Only" if avg <= 0 else "Healthy Stock"
            rows.append({
                "product_id": str(p.product_id),
                "product_name": p.name,
                "product_code": p.code,
                "product_group": p.product_group_id.group_name if p.product_group_id else None,
                "unit": p.unit_options_id.unit_name if p.unit_options_id else None,
                "current_stock": current,
                "average_sales": avg,
                "stock_difference": diff,
                "stock_status": st,
                "status_message": msg,
            })

        rows.sort(key=lambda r: (rank.get(r["stock_status"], 3), -r["average_sales"]))
        summary = {
            "total_products": len(rows),
            "critical": red,
            "warning": yellow,
            "healthy": green,
        }
        data, total = paginate_list(rows, page, limit)
        resp = build_report_response(
            report_type=self.report_type, report_label=self.report_label,
            data=data, summary=summary, filters_applied=filters_applied,
            page=page, limit=limit, total=total,
        )
        self._store(request, cache_params, resp.data)
        return resp
