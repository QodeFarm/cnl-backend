from datetime import datetime, timezone
from rest_framework.response import Response
from rest_framework import status


def build_report_response(
    *,
    report_type: str,
    report_label: str,
    data: list,
    summary: dict,
    filters_applied: dict,
    page: int,
    limit: int,
    total: int,
    status_code=status.HTTP_200_OK,
    extra: dict = None,
):
    """
    Single standard response shape for every report endpoint.

    Frontend can always rely on this structure:
      success, report_type, report_label, generated_at,
      filters_applied, summary, data, pagination
    """
    total_pages = max(1, -(-total // limit)) if limit > 0 else 1  # ceiling division

    payload = {
        "success": status_code < 400,
        "message": "success",
        "report_type": report_type,
        "report_label": report_label,
        "generated_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "filters_applied": filters_applied or {},
        "summary": summary or {},
        "data": data,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
        },
        # TaTable compatibility
        "count": total,
        "totalCount": total,
        "page": page,
        "limit": limit,
    }

    if extra:
        payload.update(extra)

    return Response(payload, status=status_code)


def build_error_response(message: str, errors=None, status_code=status.HTTP_400_BAD_REQUEST):
    return Response(
        {
            "success": False,
            "message": message,
            "errors": errors or {},
        },
        status=status_code,
    )
