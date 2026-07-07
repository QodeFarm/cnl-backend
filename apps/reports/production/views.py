"""
Production reports — Material Issue / Material Received flow.

Field reality (verified against apps/production/models.py + tenant DBs):
  MaterialIssue:      issue_no, issue_date, production_floor_id, order_status_id, is_deleted
  MaterialIssueItem:  material_issue_id, product_id, description, unit_options_id,
                      quantity, rate, amount, hsn_code, brand
  MaterialReceived:   receipt_no, receipt_date, production_floor_id, is_deleted
  MaterialReceivedItem: same shape as MaterialIssueItem
  WorkOrder (work_orders):  product_id, status_id, quantity, completed_qty,
                            start_date, end_date, is_deleted
  BillOfMaterials (bill_of_materials): product_id, reference_id, quantity,
                            unit_cost, total_cost, is_deleted
  (Machine has no rows in the active tenants → no Machine Utilization report.)
"""

from decimal import Decimal

from django.db.models import Count, Sum, Value, DecimalField
from django.db.models.functions import Coalesce

from rest_framework.response import Response

from apps.reports.base.views import BaseReportView
from apps.reports.base.pagination import get_page_and_limit, paginate_list
from apps.reports.base.response import build_report_response
from apps.reports.production.filters import (
    MaterialIssueFilter, MaterialReceivedFilter, WorkOrderFilter, BOMFilter,
)
from apps.production.models import (
    MaterialIssueItem, MaterialReceivedItem, WorkOrder, BillOfMaterials,
)

ZERO = Value(Decimal("0.00"), output_field=DecimalField(max_digits=18, decimal_places=2))


class MaterialIssueRegisterView(BaseReportView):
    """Raw material issued to production floors — one row per issued item."""
    report_type = "material_issue_register"
    report_label = "Material Issue Register"
    module = "production"
    filter_class = MaterialIssueFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            MaterialIssueItem.objects
            .filter(material_issue_id__is_deleted=False)
            .select_related(
                "material_issue_id",
                "material_issue_id__production_floor_id",
                "product_id",
                "unit_options_id",
            )
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_items=Count("material_issue_item_id"),
            total_qty=Coalesce(Sum("quantity"), ZERO),
            total_amount=Coalesce(Sum("amount"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for it in queryset:
            mi = it.material_issue_id
            rows.append({
                "material_issue_item_id": str(it.material_issue_item_id),
                "issue_no": mi.issue_no if mi else None,
                "issue_date": mi.issue_date if mi else None,
                "production_floor": (
                    mi.production_floor_id.name if mi and mi.production_floor_id else None
                ),
                "product_name": it.product_id.name if it.product_id else (it.description or None),
                "product_code": it.product_id.code if it.product_id else None,
                "unit": it.unit_options_id.unit_name if it.unit_options_id else None,
                "quantity": it.quantity,
                "rate": it.rate,
                "amount": it.amount,
            })
        return rows


class MaterialReceivedRegisterView(BaseReportView):
    """Finished/semi-finished goods received from production — one row per item."""
    report_type = "material_received_register"
    report_label = "Material Received Register"
    module = "production"
    filter_class = MaterialReceivedFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            MaterialReceivedItem.objects
            .filter(material_received_id__is_deleted=False)
            .select_related(
                "material_received_id",
                "material_received_id__production_floor_id",
                "product_id",
                "unit_options_id",
            )
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_items=Count("material_received_item_id"),
            total_qty=Coalesce(Sum("quantity"), ZERO),
            total_amount=Coalesce(Sum("amount"), ZERO),
        )

    def serialize(self, queryset):
        rows = []
        for it in queryset:
            mr = it.material_received_id
            rows.append({
                "material_received_item_id": str(it.material_received_item_id),
                "receipt_no": mr.receipt_no if mr else None,
                "receipt_date": mr.receipt_date if mr else None,
                "production_floor": (
                    mr.production_floor_id.name if mr and mr.production_floor_id else None
                ),
                "product_name": it.product_id.name if it.product_id else (it.description or None),
                "product_code": it.product_id.code if it.product_id else None,
                "unit": it.unit_options_id.unit_name if it.unit_options_id else None,
                "quantity": it.quantity,
                "rate": it.rate,
                "amount": it.amount,
            })
        return rows


class RawMaterialConsumptionView(BaseReportView):
    """Total raw material consumed (issued) grouped by product."""
    report_type = "raw_material_consumption"
    report_label = "Raw Material Consumption"
    module = "production"
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
            return Response(cached)   # never `return cached` — CLAUDE gotcha 1

        f = MaterialIssueFilter(flat)
        base_qs = (
            MaterialIssueItem.objects.using(db_alias)
            .filter(material_issue_id__is_deleted=False)
            .select_related("product_id")
        )
        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        summary_agg = base_qs.aggregate(
            total_qty=Coalesce(Sum("quantity"), ZERO),
            total_amount=Coalesce(Sum("amount"), ZERO),
        )

        agg = (
            base_qs
            .values("product_id", "product_id__name", "product_id__code")
            .annotate(
                total_qty=Coalesce(Sum("quantity"), ZERO),
                total_amount=Coalesce(Sum("amount"), ZERO),
                issue_count=Count("material_issue_id", distinct=True),
            )
            .order_by("-total_qty")
        )
        rows = [{
            "product_id": str(r["product_id"]) if r["product_id"] else "",
            "product_name": r["product_id__name"] or "",
            "product_code": r["product_id__code"],
            "total_qty": r["total_qty"],
            "total_amount": r["total_amount"],
            "issue_count": r["issue_count"],
        } for r in agg]

        summary = {
            "total_products": len(rows),
            "total_qty": str(summary_agg["total_qty"]),
            "total_amount": str(summary_agg["total_amount"]),
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


# =============================================================
# Work Order Status / Production Summary / BOM
# (tables: work_orders, bill_of_materials, production_statuses)
# =============================================================

class WorkOrderStatusView(BaseReportView):
    """All work orders with quantity, completed and balance per product."""
    report_type = "work_order_status"
    report_label = "Work Order Status"
    module = "production"
    filter_class = WorkOrderFilter
    cache_ttl = 300

    def get_queryset(self, request):
        return (
            WorkOrder.objects
            .filter(is_deleted=False)
            .select_related("product_id", "status_id")
        )

    def get_summary(self, queryset):
        return queryset.aggregate(
            total_work_orders=Count("work_order_id"),
            total_qty=Coalesce(Sum("quantity"), Value(0)),
            total_completed=Coalesce(Sum("completed_qty"), Value(0)),
        )

    def serialize(self, queryset):
        rows = []
        for wo in queryset:
            qty = wo.quantity or 0
            done = wo.completed_qty or 0
            rows.append({
                "work_order_id": str(wo.work_order_id),
                "product_name": wo.product_id.name if wo.product_id else None,
                "product_code": wo.product_id.code if wo.product_id else None,
                "status": wo.status_id.status_name if wo.status_id else None,
                "quantity": qty,
                "completed_qty": done,
                "balance_qty": max(qty - done, 0),
                "start_date": wo.start_date,
                "end_date": wo.end_date,
            })
        return rows


class ProductionSummaryView(BaseReportView):
    """Work orders grouped by production status — count, qty and completed."""
    report_type = "production_summary"
    report_label = "Production Summary"
    module = "production"
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

        f = WorkOrderFilter(flat)
        base_qs = WorkOrder.objects.using(db_alias).filter(is_deleted=False).select_related("status_id")
        base_qs = f.apply(base_qs)
        filters_applied = f.get_applied_filters()

        agg = (
            base_qs
            .values("status_id__status_name")
            .annotate(
                work_orders=Count("work_order_id"),
                total_qty=Coalesce(Sum("quantity"), Value(0)),
                completed_qty=Coalesce(Sum("completed_qty"), Value(0)),
            )
            .order_by("-work_orders")
        )
        rows = [{
            "status": r["status_id__status_name"] or "Unassigned",
            "work_orders": r["work_orders"],
            "total_qty": r["total_qty"],
            "completed_qty": r["completed_qty"],
            "balance_qty": max((r["total_qty"] or 0) - (r["completed_qty"] or 0), 0),
        } for r in agg]

        summary = {
            "total_statuses": len(rows),
            "total_work_orders": sum(r["work_orders"] for r in rows),
            "total_qty": sum(r["total_qty"] for r in rows),
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


class BOMReportView(BaseReportView):
    """Bill of Materials — component lines with quantity and cost per product."""
    report_type = "bom_report"
    report_label = "Bill of Materials"
    module = "production"
    filter_class = BOMFilter
    cache_ttl = 600

    def get_queryset(self, request):
        return (
            BillOfMaterials.objects
            .filter(is_deleted=False)
            .select_related("product_id")
        )

    def get_summary(self, queryset):
        agg = queryset.aggregate(
            total_lines=Count("material_id"),
            total_qty=Coalesce(Sum("quantity"), Value(0)),
            total_cost=Coalesce(Sum("total_cost"), ZERO),
        )
        # surface BOM lines whose cost was never entered, so a low total is read
        # as "cost not set" rather than complete (honest empty state — flow.md).
        agg["unpriced_lines"] = queryset.exclude(unit_cost__gt=0).count()
        return agg

    def serialize(self, queryset):
        rows = []
        for b in queryset:
            # unit_cost not entered (0/null) → show "cost not set" (null), never ₹0.
            has_cost = b.unit_cost and b.unit_cost > 0
            rows.append({
                "material_id": str(b.material_id),
                "product_name": b.product_id.name if b.product_id else None,
                "product_code": b.product_id.code if b.product_id else None,
                "reference_id": b.reference_id,
                "quantity": b.quantity,
                "unit_cost": b.unit_cost if has_cost else None,
                "total_cost": b.total_cost if has_cost else None,
            })
        return rows
