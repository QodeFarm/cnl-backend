from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from apps.products.filters import ProductsFilter
from config.utils_filter_methods import list_filtered_objects, filter_response
from apps.inventory.filters import WarehouseLocationsFilter, WarehousesFilter, StockForecastReportFilter
from .models import *
from .serializers import *
from config.utils_methods import *
from config.utils_variables import *
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter
from apps.products.models import Products
from apps.sales.models import SaleInvoiceItems, SaleOrderItems
from django.db.models import Sum, Q
from django.db.models.functions import Coalesce
from decimal import Decimal
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


# Create your views here.
class WarehousesViewSet(viewsets.ModelViewSet):
    queryset = Warehouses.objects.all().order_by('is_deleted', '-created_at')	
    serializer_class = WarehousesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = WarehousesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Warehouses,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class WarehouseLocationsViewSet(viewsets.ModelViewSet):
    queryset = WarehouseLocations.objects.all().order_by('is_deleted', '-created_at')	
    serializer_class = WarehouseLocationsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = WarehouseLocationsFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, WarehouseLocations,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class InventoryBlockConfigViewSet(viewsets.ModelViewSet):
    queryset = InventoryBlockConfig.objects.all()
    serializer_class = InventoryBlockConfigSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class BlockedInventoryViewSet(viewsets.ModelViewSet):
    queryset = BlockedInventory.objects.all()
    serializer_class = BlockedInventorySerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class StockForecastReportView(APIView):
    """
    Stock Forecast Report API - Shows product-wise stock status with avg sales comparison.
    Uses Quick Period filter for dynamic date range selection.
    
    Quick Period Options:
    - current_month: Last 30 days (1 month avg)
    - last_month: Previous month (1 month avg)
    - last_six_months: Last 180 days (6 month avg) - DEFAULT
    - current_quarter: Last 90 days (3 month avg)
    - year_to_date: Last 365 days (12 month avg)
    - last_year: Previous year (12 month avg)
    """

    def get(self, request, *args, **kwargs):    
        try:
            # Get params
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))
            status_filter = request.query_params.get('status', None)
            
            # Default period_days (6 months)
            period_days = 180
            
            # Check for custom period_days parameter (backward compatibility)
            if request.query_params.get('period_days'):
                period_days = int(request.query_params.get('period_days', 180))
            
            # Base queryset - ALL products (before any filter)
            base_queryset = Products.objects.filter(is_deleted=False).order_by('-created_at')
            
            # Get total count BEFORE pagination
            total_products_count = base_queryset.count()
            
            # Apply filters using StockForecastReportFilter
            filterset = None
            queryset = base_queryset
            if request.query_params:
                filterset = StockForecastReportFilter(request.GET, queryset=base_queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
                    
                    # Get period_days from filter if Quick Period was selected
                    if hasattr(filterset, 'period_days'):
                        period_days = filterset.period_days

            # Date range calculation for sales data
            end_date = datetime.now().date()
            start_date = end_date - timedelta(days=period_days)

            # Get sales data from BOTH SaleInvoiceItems AND SaleOrderItems
            invoice_sales = SaleInvoiceItems.objects.filter(
                sale_invoice_id__invoice_date__gte=start_date,
                sale_invoice_id__invoice_date__lte=end_date
            ).values('product_id').annotate(
                total_sales=Coalesce(Sum('quantity'), Decimal('0'))
            )

            order_sales = SaleOrderItems.objects.filter(
                sale_order_id__order_date__gte=start_date,
                sale_order_id__order_date__lte=end_date
            ).values('product_id').annotate(
                total_sales=Coalesce(Sum('quantity'), 0)
            )

            # Build sales dict - combine both invoice and order sales
            sales_dict = {}
            for item in invoice_sales:
                if item['product_id']:
                    pid_str = str(item['product_id']).replace('-', '')
                    sales_dict[pid_str] = Decimal(item['total_sales'])
            
            for item in order_sales:
                if item['product_id']:
                    pid_str = str(item['product_id']).replace('-', '')
                    if pid_str in sales_dict:
                        sales_dict[pid_str] += Decimal(item['total_sales'])
                    else:
                        sales_dict[pid_str] = Decimal(item['total_sales'])

            # Serialize products - Pass both sales_dict AND period_days
            serializer = ProductStockForecastSerializer(
                queryset, 
                many=True, 
                context={
                    'sales_dict': sales_dict,
                    'period_days': period_days
                }
            )

            # Get total count from filterset (set by filter_by_limit) or use total_products_count
            total_count = getattr(filterset, 'total_count', total_products_count) if filterset else total_products_count

            logger.info(f"Stock forecast report data retrieved successfully. Period: {period_days} days")
            
            # Use total_count for both 'count' and 'totalCount' to match Sale Order API format
            # This ensures pagination works correctly (shows "Total Records - 26" not "Total Records - 10")
            response = filter_response(
                total_count,  # Changed from len(serializer.data) to total_count for pagination
                "Success",
                serializer.data,
                page,
                limit,
                total_count,
                status.HTTP_200_OK
            )
            
            # Add period info to response for frontend reference
            response.data['period_info'] = {
                'period_days': period_days,
                'start_date': str(start_date),
                'end_date': str(end_date),
                'months': round(period_days / 30, 1)
            }
            
            return response

        except Products.DoesNotExist:
            logger.error("Products do not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"Stock forecast report error: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)