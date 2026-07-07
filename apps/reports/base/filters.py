"""
Layered Report Filter System
==============================
Every report applies filters in four layers, in order:

  Layer 1 — Date / Period
      from_date, to_date, period
      Configurable via `date_field` class attribute on each filter subclass.

  Layer 2 — Primary Entity
      customer, customer_id, product, product_id, salesperson_id, vendor, vendor_id
      Each report subclass declares which entity params it supports.

  Layer 3 — Secondary / Drill-down
      status, bill_type, sale_type, city, state, min_amount, max_amount, etc.
      Defined per-report in the subclass.

  Layer 4 — Presentation
      sort_by, sort_order, page, limit
      Always available on every report.

Usage in a report view:
    filter_class = SalesRegisterFilter        # subclass of BaseReportFilter
    f = filter_class(request.query_params)
    queryset = f.apply(base_queryset)
    filters_applied = f.get_applied_filters()
"""

import datetime
import logging
from django.db.models import Q
from django.utils import timezone

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# Period presets (same periods as existing code)
# ─────────────────────────────────────────────
PERIOD_CHOICES = [
    "today",
    "yesterday",
    "last_week",
    "current_week",
    "current_month",
    "last_month",
    "last_three_months",
    "last_six_months",
    "current_quarter",
    "last_quarter",
    "year_to_date",
    "last_year",
    "custom",
]

SORT_ORDER_CHOICES = ("asc", "desc")


def _resolve_period(period: str):
    """
    Translate a period preset to (start_date, end_date).
    Returns (None, None) if period is unrecognised.
    """
    today = timezone.now().date()

    if period == "today":
        return today, today

    if period == "yesterday":
        d = today - datetime.timedelta(days=1)
        return d, d

    if period == "last_week":
        start = today - datetime.timedelta(days=today.weekday() + 7)
        return start, start + datetime.timedelta(days=6)

    if period == "current_week":
        start = today - datetime.timedelta(days=today.weekday())
        return start, today

    if period == "current_month":
        return today.replace(day=1), today

    if period == "last_month":
        first_this = today.replace(day=1)
        last_prev = first_this - datetime.timedelta(days=1)
        return last_prev.replace(day=1), last_prev

    if period == "last_three_months":
        return today - datetime.timedelta(days=90), today

    if period == "last_six_months":
        return today - datetime.timedelta(days=180), today

    if period == "current_quarter":
        q = (today.month - 1) // 3
        start_month = q * 3 + 1
        return today.replace(month=start_month, day=1), today

    if period == "last_quarter":
        q = (today.month - 1) // 3
        if q == 0:
            start_month = 10
            year = today.year - 1
        else:
            start_month = (q - 1) * 3 + 1
            year = today.year
        start = today.replace(year=year, month=start_month, day=1)
        end_month = start_month + 2
        if end_month > 12:
            end_month -= 12
        import calendar
        last_day = calendar.monthrange(year if end_month >= start_month else today.year, end_month)[1]
        end = datetime.date(year if end_month >= start_month else today.year, end_month, last_day)
        return start, end

    if period == "year_to_date":
        # Financial year starts April 1
        fy_start_month = 4
        if today.month >= fy_start_month:
            return today.replace(month=fy_start_month, day=1), today
        return today.replace(year=today.year - 1, month=fy_start_month, day=1), today

    if period == "last_year":
        fy_start_month = 4
        if today.month >= fy_start_month:
            start = today.replace(year=today.year - 1, month=fy_start_month, day=1)
            end = today.replace(month=fy_start_month, day=1) - datetime.timedelta(days=1)
        else:
            start = today.replace(year=today.year - 2, month=fy_start_month, day=1)
            end = today.replace(year=today.year - 1, month=fy_start_month, day=1) - datetime.timedelta(days=1)
        return start, end

    return None, None


class BaseReportFilter:
    """
    Base class for all report filters.

    Subclass and set:
        date_field           — model field name for date range (e.g. 'invoice_date')
        allowed_sort_fields  — list of field names allowed for sorting
        default_sort_field   — field used when no sort param is given
        default_sort_order   — 'desc' or 'asc'

        # Entity field path overrides (needed when entity is accessed via FK chain)
        customer_id_field    — e.g. 'sale_invoice_id__customer_id'
        customer_name_field  — e.g. 'sale_invoice_id__customer_id__name'
        product_id_field     — e.g. 'product_id'
        product_name_field   — e.g. 'product_id__name'
        salesperson_field    — e.g. 'order_salesman_id'
        vendor_id_field      — e.g. 'vendor_id'
        vendor_name_field    — e.g. 'vendor_id__name'

    Example subclass (item-level report that accesses customer via invoice FK):
        class SalesRegisterDetailedFilter(BaseReportFilter):
            date_field = 'sale_invoice_id__invoice_date'
            customer_id_field = 'sale_invoice_id__customer_id'
            customer_name_field = 'sale_invoice_id__customer_id__name'
            default_sort_field = 'sale_invoice_id__invoice_date'
    """

    date_field = "created_at"
    allowed_sort_fields: list = []
    default_sort_field = None
    default_sort_order = "desc"

    # Configurable entity field paths
    customer_id_field = "customer_id"
    customer_name_field = "customer_id__name"
    product_id_field = "product_id"
    product_name_field = "product_id__name"
    salesperson_field = "order_salesman_id"
    vendor_id_field = "vendor_id"
    vendor_name_field = "vendor_id__name"

    def __init__(self, params: dict):
        self.params = params
        self._applied = {}          # tracks what was actually applied

    # ─────────────────────────────────────────────
    # Public API
    # ─────────────────────────────────────────────

    def apply(self, queryset):
        """Apply all four layers in order and return the filtered queryset."""
        queryset = self._apply_date_layer(queryset)
        queryset = self._apply_entity_layer(queryset)
        queryset = self.apply_secondary_filters(queryset)   # Layer 3 — override in subclass
        queryset = self._apply_sort(queryset)
        return queryset

    def get_applied_filters(self) -> dict:
        """Return a dict of every non-empty filter that was applied (for the response)."""
        return {k: v for k, v in self._applied.items() if v not in (None, "", [], {})}

    # ─────────────────────────────────────────────
    # Layer 1 — Date / Period
    # ─────────────────────────────────────────────

    def _apply_date_layer(self, queryset):
        from_date_str = self.params.get("from_date")
        to_date_str = self.params.get("to_date")
        period = self.params.get("period", "").strip().lower()

        start_date, end_date = None, None

        if period and period != "custom" and period in PERIOD_CHOICES:
            start_date, end_date = _resolve_period(period)
            self._applied["period"] = period
        elif from_date_str or to_date_str:
            start_date = self._parse_date(from_date_str)
            end_date = self._parse_date(to_date_str)
            if start_date:
                self._applied["from_date"] = str(start_date)
            if end_date:
                self._applied["to_date"] = str(end_date)

        if start_date:
            start_dt = datetime.datetime.combine(start_date, datetime.time.min)
            queryset = queryset.filter(**{f"{self.date_field}__gte": start_dt})
        if end_date:
            end_dt = datetime.datetime.combine(end_date, datetime.time.max)
            queryset = queryset.filter(**{f"{self.date_field}__lte": end_dt})

        return queryset

    # ─────────────────────────────────────────────
    # Layer 2 — Primary Entity
    # ─────────────────────────────────────────────

    def _apply_entity_layer(self, queryset):
        # Customer filters
        customer_id = self.params.get("customer_id")
        customer_name = self.params.get("customer")
        if customer_id:
            queryset = queryset.filter(**{self.customer_id_field: customer_id})
            self._applied["customer_id"] = customer_id
        elif customer_name:
            queryset = queryset.filter(**{f"{self.customer_name_field}__icontains": customer_name})
            self._applied["customer"] = customer_name

        # Product filters
        product_id = self.params.get("product_id")
        product_name = self.params.get("product")
        if product_id:
            queryset = queryset.filter(**{self.product_id_field: product_id})
            self._applied["product_id"] = product_id
        elif product_name:
            queryset = queryset.filter(**{f"{self.product_name_field}__icontains": product_name})
            self._applied["product"] = product_name

        # Salesperson filter
        salesperson_id = self.params.get("salesperson_id")
        if salesperson_id:
            queryset = queryset.filter(**{self.salesperson_field: salesperson_id})
            self._applied["salesperson_id"] = salesperson_id

        # Vendor filters
        vendor_id = self.params.get("vendor_id")
        vendor_name = self.params.get("vendor")
        if vendor_id:
            queryset = queryset.filter(**{self.vendor_id_field: vendor_id})
            self._applied["vendor_id"] = vendor_id
        elif vendor_name:
            queryset = queryset.filter(**{f"{self.vendor_name_field}__icontains": vendor_name})
            self._applied["vendor"] = vendor_name

        return queryset

    # ─────────────────────────────────────────────
    # Layer 3 — Secondary / Drill-down (override in subclass)
    # ─────────────────────────────────────────────

    def apply_secondary_filters(self, queryset):
        """
        Override in each report's filter class to apply report-specific filters.
        This is Layer 3: status, bill_type, city, amount range, etc.
        """
        return queryset

    # ─────────────────────────────────────────────
    # Layer 4 — Sorting
    # ─────────────────────────────────────────────

    def _apply_sort(self, queryset):
        sort_by = self.params.get("sort_by", self.default_sort_field)
        sort_order = self.params.get("sort_order", self.default_sort_order).lower()

        if sort_order not in SORT_ORDER_CHOICES:
            sort_order = self.default_sort_order

        if sort_by and (not self.allowed_sort_fields or sort_by in self.allowed_sort_fields):
            field = f"-{sort_by}" if sort_order == "desc" else sort_by
            try:
                queryset = queryset.order_by(field)
                self._applied["sort_by"] = sort_by
                self._applied["sort_order"] = sort_order
            except Exception:
                # Invalid sort field — fall back silently
                if self.default_sort_field:
                    field = f"-{self.default_sort_field}" if self.default_sort_order == "desc" else self.default_sort_field
                    queryset = queryset.order_by(field)
        elif self.default_sort_field:
            field = f"-{self.default_sort_field}" if self.default_sort_order == "desc" else self.default_sort_field
            queryset = queryset.order_by(field)

        return queryset

    # ─────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────

    @staticmethod
    def _parse_date(value):
        if not value:
            return None
        for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
            try:
                return datetime.datetime.strptime(value.strip(), fmt).date()
            except (ValueError, AttributeError):
                continue
        logger.warning("Could not parse date: %s", value)
        return None

    def get_search_query(self, search_fields: list) -> Q:
        """
        Build a Q object for a global text search across given fields.
        Called by subclasses in apply_secondary_filters if needed.
        """
        search = self.params.get("search", "").strip()
        if not search:
            return Q()
        q = Q()
        for field in search_fields:
            q |= Q(**{f"{field}__icontains": search})
        if search:
            self._applied["search"] = search
        return q
