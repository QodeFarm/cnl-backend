"""
Inventory report filters.

Stock reports query the Products table directly (current stock = Products.balance),
so the entity is the PRODUCT and its group/category/brand live straight on Products
(product_group_id, category_id, brand_id) — not via a product_id__ FK chain.
There is no date filter on stock reports (stock is a current snapshot).
"""

from apps.reports.base.filters import BaseReportFilter


class InventoryProductFilter(BaseReportFilter):
    """Filter for Products-level stock reports (Summary / Valuation / Reorder)."""
    date_field = "created_at"   # rarely used; stock reports are a current snapshot
    product_id_field = "product_id"
    product_name_field = "name"
    default_sort_field = "name"
    default_sort_order = "asc"
    allowed_sort_fields = [
        "name", "code", "balance", "minimum_level", "purchase_rate", "sales_rate",
    ]

    def apply_secondary_filters(self, queryset):
        params = self.params

        product_group_id = params.get("product_group_id", "").strip()
        if product_group_id:
            queryset = queryset.filter(product_group_id=product_group_id)
            self._applied["product_group_id"] = product_group_id

        product_category_id = params.get("product_category_id", "").strip()
        if product_category_id:
            queryset = queryset.filter(category_id=product_category_id)
            self._applied["product_category_id"] = product_category_id

        product_brand_id = params.get("product_brand_id", "").strip()
        if product_brand_id:
            queryset = queryset.filter(brand_id=product_brand_id)
            self._applied["product_brand_id"] = product_brand_id

        status = params.get("status", "").strip()
        if status:
            queryset = queryset.filter(status__iexact=status)
            self._applied["status"] = status

        search_q = self.get_search_query(["name", "code", "hsn_code"])
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset


class StockMovementFilter(BaseReportFilter):
    """Filter for the Stock Movement ledger (StockJournal: Receive / Issue rows)."""
    date_field = "created_at"
    product_id_field = "product_id"
    product_name_field = "product_id__name"
    default_sort_field = "created_at"
    default_sort_order = "desc"
    allowed_sort_fields = ["created_at", "quantity", "product_id__name"]

    def apply_secondary_filters(self, queryset):
        params = self.params

        transaction_type = params.get("transaction_type", "").strip()
        if transaction_type:
            queryset = queryset.filter(transaction_type__iexact=transaction_type)
            self._applied["transaction_type"] = transaction_type

        search_q = self.get_search_query(
            ["product_id__name", "product_id__code", "reference_id", "remarks"]
        )
        if search_q:
            queryset = queryset.filter(search_q)

        return queryset
