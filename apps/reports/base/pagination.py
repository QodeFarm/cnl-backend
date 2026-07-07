"""
Report pagination utilities.

All report views use page + limit style pagination.
Max limit is capped at 1000 to prevent runaway queries.
Export requests (export=csv|excel|pdf) bypass the limit cap.
"""

DEFAULT_PAGE = 1
DEFAULT_LIMIT = 50
MAX_LIMIT = 1000


def get_page_and_limit(request):
    """
    Extract and validate page / limit from request query params.
    Returns (page: int, limit: int).
    """
    try:
        page = max(1, int(request.query_params.get("page", DEFAULT_PAGE)))
    except (ValueError, TypeError):
        page = DEFAULT_PAGE

    try:
        limit_raw = request.query_params.get("limit") or request.query_params.get("page_size", DEFAULT_LIMIT)
        limit = int(limit_raw)
        limit = max(1, min(limit, MAX_LIMIT))
    except (ValueError, TypeError):
        limit = DEFAULT_LIMIT

    return page, limit


def paginate_queryset(queryset, page: int, limit: int):
    """
    Slice the queryset for the given page/limit.
    Returns (paginated_queryset, total_count).

    total_count is evaluated before slicing so the frontend
    can calculate total_pages without an extra request.
    """
    total_count = queryset.count()
    start = (page - 1) * limit
    end = start + limit
    return queryset[start:end], total_count


def paginate_list(data: list, page: int, limit: int):
    """
    Paginate a plain Python list (for already-aggregated in-memory data).
    Returns (paginated_list, total_count).
    """
    total_count = len(data)
    start = (page - 1) * limit
    end = start + limit
    return data[start:end], total_count
