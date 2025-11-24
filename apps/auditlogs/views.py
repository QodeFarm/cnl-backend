from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from apps.auditlogs.filters import AuditLogFilter
from config.utils_filter_methods import filter_response
from config.utils_methods import build_response
from .models import AuditLog  # Or ActivityLog if renamed
from .serializers import AuditLogSerializer

class AuditLogView(APIView):
    """
    GET: Returns all audit logs, sorted by latest timestamp.
    """

    def get(self, request):
        try:
            queryset = AuditLog.objects.all()

            # Apply filters
            if request.query_params:
                filterset = AuditLogFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs

            # Handle default sorting (if no slicing applied by global filter)
            if not queryset.query.is_sliced:
                queryset = queryset.order_by('-created_at')

            # Manual pagination after filtering and sorting
            page = int(request.GET.get('page', 1))
            limit = int(request.GET.get('limit', 10))
            offset = (page - 1) * limit
            paginated_queryset = queryset[offset:offset + limit]
            total_count = queryset.count()

            # Serialize filtered/paginated data
            serializer = AuditLogSerializer(paginated_queryset, many=True)
            return filter_response(
                queryset.count(),
                "Success",
                serializer.data,
                page=page,
                limit=limit,
                total_count=total_count,
                status_code=status.HTTP_200_OK
            )

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
