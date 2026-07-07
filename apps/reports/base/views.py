"""
BaseReportView
==============
All report views inherit from this class.  Each subclass only needs to:

  1. Set class attributes:
       report_type      — unique string id, e.g. 'sales_register'
       report_label     — human label, e.g. 'Sales Register'
       module           — module name for cache key, e.g. 'sales'
       serializer_class — DRF serializer for the data rows
       filter_class     — subclass of BaseReportFilter
       cache_ttl        — seconds to cache (0 = no cache)

  2. Override:
       get_queryset(request)   — return the base queryset (un-filtered, un-paginated)
       get_summary(queryset)   — return dict of KPI totals shown above the table
       serialize(queryset)     — if custom serialization is needed (default uses serializer_class)

The base handles: filter → paginate → (optionally cache) → respond
"""

import logging
from rest_framework.views import APIView
from rest_framework import status

from apps.reports.base.cache import get_cached, set_cached
from apps.reports.base.pagination import get_page_and_limit, paginate_queryset
from apps.reports.base.response import build_report_response, build_error_response

logger = logging.getLogger(__name__)


class BaseReportView(APIView):
    # ── required on every subclass ──────────────────
    report_type: str = None
    report_label: str = ""
    module: str = "reports"
    serializer_class = None
    filter_class = None

    # ── optional tuning ─────────────────────────────
    cache_ttl: int = 300        # 0 = disable cache for this report
    db_alias: str = None        # None = use default / middleware-selected DB

    # ─────────────────────────────────────────────────
    # Subclass API
    # ─────────────────────────────────────────────────

    def get_queryset(self, request):
        """
        Return the raw, un-filtered queryset for this report.
        Apply select_related / prefetch_related here for performance.
        Override in every subclass.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} must implement get_queryset()"
        )

    def get_summary(self, queryset) -> dict:
        """
        Return a dict of KPI totals that appear above the data table.
        Override in each report to return meaningful aggregates.
        Default: total record count only.
        """
        return {"total_records": queryset.count()}

    def serialize(self, queryset) -> list:
        """
        Serialize the (already filtered + paginated) queryset to a list of dicts.
        Default: uses self.serializer_class with many=True.
        Override for custom serialization (e.g., pure .values() annotated querysets).
        """
        if self.serializer_class is None:
            raise NotImplementedError(
                f"{self.__class__.__name__} must set serializer_class or override serialize()"
            )
        serializer = self.serializer_class(queryset, many=True)
        return serializer.data

    # ─────────────────────────────────────────────────
    # Request pipeline — do not override
    # ─────────────────────────────────────────────────

    def get(self, request, *args, **kwargs):
        try:
            return self._handle_report(request)
        except Exception as exc:
            logger.exception("Unhandled error in report %s: %s", self.report_type, exc)
            return build_error_response(
                message="An error occurred while generating the report.",
                errors={"detail": str(exc)},
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _handle_report(self, request):
        params = dict(request.query_params)
        # query_params returns lists for each key; flatten single-value keys
        flat_params = {k: v[0] if isinstance(v, list) and len(v) == 1 else v
                       for k, v in params.items()}

        page, limit = get_page_and_limit(request)
        db_alias = self.db_alias or self._get_db_alias(request)

        # ── Cache check ───────────────────────────────
        cache_params = {**flat_params, "_page": page, "_limit": limit}
        if self.cache_ttl > 0:
            cached = get_cached(self.module, self.report_type, db_alias, cache_params)
            if cached is not None:
                from rest_framework.response import Response
                return Response(cached, status=status.HTTP_200_OK)

        # ── Build queryset ────────────────────────────
        queryset = self.get_queryset(request)
        if db_alias:
            queryset = queryset.using(db_alias)

        # ── Apply filters (all 4 layers) ──────────────
        filters_applied = {}
        if self.filter_class:
            report_filter = self.filter_class(flat_params)
            queryset = report_filter.apply(queryset)
            filters_applied = report_filter.get_applied_filters()

        # ── Summary KPIs (on full filtered set, before pagination) ──
        summary = self.get_summary(queryset)

        # ── Paginate ──────────────────────────────────
        paginated_qs, total = paginate_queryset(queryset, page, limit)

        # ── Serialize ─────────────────────────────────
        data = list(self.serialize(paginated_qs))

        # ── Build response ────────────────────────────
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

        # ── Cache result ──────────────────────────────
        if self.cache_ttl > 0:
            set_cached(self.module, self.report_type, db_alias, cache_params,
                       response_obj.data, self.cache_ttl)

        return response_obj

    # ─────────────────────────────────────────────────
    # Helpers
    # ─────────────────────────────────────────────────

    @staticmethod
    def _get_db_alias(request):
        """
        Respect the database already selected by DatabaseMiddleware.
        Falls back to None (Django default) if not set.
        """
        return getattr(request, "db_alias", None)
