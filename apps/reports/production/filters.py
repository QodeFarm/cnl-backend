"""
Production report filters.

Only the Material Issue / Material Received flow exists with real data
(work-order / BOM tables are not migrated in any tenant), so these filters
target the item tables joined to their headers.
"""

from apps.reports.base.filters import BaseReportFilter


class MaterialIssueFilter(BaseReportFilter):
    """Item-level filter for the Material Issue Register / Raw Material Consumption."""
    date_field = "material_issue_id__issue_date"
    product_id_field = "product_id"
    product_name_field = "product_id__name"
    default_sort_field = "material_issue_id__issue_date"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "material_issue_id__issue_date", "quantity", "amount", "product_id__name",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        floor = params.get("production_floor_id", "").strip()
        if floor:
            queryset = queryset.filter(material_issue_id__production_floor_id=floor)
            self._applied["production_floor_id"] = floor

        search_q = self.get_search_query([
            "material_issue_id__issue_no", "product_id__name",
            "product_id__code", "description", "brand",
        ])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class WorkOrderFilter(BaseReportFilter):
    """Work Order Status / Production Summary (WorkOrder rows)."""
    date_field = "start_date"
    product_id_field = "product_id"
    product_name_field = "product_id__name"
    default_sort_field = "created_at"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "created_at", "start_date", "end_date", "quantity", "completed_qty", "product_id__name",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        status = params.get("status", "").strip()
        if status:
            queryset = queryset.filter(status_id__status_name__iexact=status)
            self._applied["status"] = status

        search_q = self.get_search_query(["product_id__name", "product_id__code", "remarks"])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class BOMFilter(BaseReportFilter):
    """Bill of Materials report (BillOfMaterials line items)."""
    date_field = "created_at"
    product_id_field = "product_id"
    product_name_field = "product_id__name"
    default_sort_field = "created_at"
    default_sort_order = "desc"
    allowed_sort_fields = ["created_at", "quantity", "total_cost", "product_id__name"]

    def apply_secondary_filters(self, queryset):
        search_q = self.get_search_query(
            ["product_id__name", "product_id__code", "reference_id", "notes"]
        )
        if search_q:
            queryset = queryset.filter(search_q)
        return queryset


class MaterialReceivedFilter(BaseReportFilter):
    """Item-level filter for the Material Received Register."""
    date_field = "material_received_id__receipt_date"
    product_id_field = "product_id"
    product_name_field = "product_id__name"
    default_sort_field = "material_received_id__receipt_date"
    default_sort_order = "desc"
    allowed_sort_fields = [
        "material_received_id__receipt_date", "quantity", "amount", "product_id__name",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        floor = params.get("production_floor_id", "").strip()
        if floor:
            queryset = queryset.filter(material_received_id__production_floor_id=floor)
            self._applied["production_floor_id"] = floor

        search_q = self.get_search_query([
            "material_received_id__receipt_no", "product_id__name",
            "product_id__code", "description", "brand",
        ])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset
