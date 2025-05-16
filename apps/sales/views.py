from datetime import timedelta
from apps.users.models import User
from itertools import chain
from config.utils_db_router import set_db
from config.utils_methods import previous_product_instance_verification, product_stock_verification, update_multi_instances, update_product_stock, validate_input_pk, delete_multi_instance, generic_data_creation, get_object_or_none, list_all_objects, create_instance, update_instance, build_response, validate_multiple_data, validate_order_type, validate_payload_data, validate_put_method_data
from config.utils_filter_methods import filter_response, list_filtered_objects
from apps.inventory.models import BlockedInventory, InventoryBlockConfig
from .models import PaymentTransactions, SaleInvoiceOrders, OrderStatuses
from apps.customfields.serializers import CustomFieldValueSerializer
from apps.finance.serializers import JournalEntryLinesSerializer
from django_filters.rest_framework import DjangoFilterBackend
from apps.products.models import Products, ProductVariation
from apps.finance.views import JournalEntryLinesAPIView
from django.core.exceptions import  ObjectDoesNotExist
from apps.customfields.models import CustomFieldValue
from apps.customer.views import CustomerBalanceView
from rest_framework.filters import OrderingFilter
from apps.customer.models import CustomerBalance
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status
from apps.masters.models import OrderTypes
from decimal import Decimal, ROUND_HALF_UP
from rest_framework.views import APIView
from django.utils import timezone
from django.db import DEFAULT_DB_ALIAS, connections, transaction
from rest_framework import status
from django.db.models import Sum
from django.http import Http404
from django.db.models import F
from datetime import datetime, timedelta
from django.apps import apps
from decimal import Decimal
from .serializers import *
from .filters import *
import traceback
import logging
import uuid
from django.db.models import Sum, F, Count,ExpressionWrapper,Value



workflow_progression_dict = {}
# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)


class SaleOrderView(viewsets.ModelViewSet):
    queryset = SaleOrder.objects.all().order_by('-created_at')
    serializer_class = SaleOrderSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = SaleOrderFilter
    ordering_fields = ['num_employees', 'created_at', 'updated_at', 'name']
    
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SaleInvoiceItemsView(viewsets.ModelViewSet):
    queryset = SaleInvoiceItems.objects.all()
    serializer_class = SaleInvoiceItemsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SalesPriceListView(viewsets.ModelViewSet):
    queryset = SalesPriceList.objects.all()
    serializer_class = SalesPriceListSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SaleOrderItemsView(viewsets.ModelViewSet):
    queryset = SaleOrderItems.objects.all()
    serializer_class = SaleOrderItemsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleOrdersItemsilter

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class SaleInvoiceOrdersView(viewsets.ModelViewSet):
    queryset = SaleInvoiceOrders.objects.all()
    serializer_class = SaleInvoiceOrdersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleInvoiceOrdersFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class SaleReturnOrdersView(viewsets.ModelViewSet):
    queryset = SaleReturnOrders.objects.all()
    serializer_class = SaleReturnOrdersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleReturnOrdersFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class SaleReturnItemsView(viewsets.ModelViewSet):
    queryset = SaleReturnItems.objects.all()
    serializer_class = SaleReturnItemsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class OrderAttachmentsView(viewsets.ModelViewSet):
    queryset = OrderAttachments.objects.all()
    serializer_class = OrderAttachmentsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class OrderShipmentsView(viewsets.ModelViewSet):
    queryset = OrderShipments.objects.all()
    serializer_class = OrderShipmentsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class QuickPacksView(viewsets.ModelViewSet):
    queryset = QuickPacks.objects.all()
    serializer_class = QuickPackSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = QuickPacksFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


class QuickPacksItemsView(viewsets.ModelViewSet):
    queryset = QuickPackItems.objects.all()
    serializer_class = QuickPackItemSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class SaleCreditNoteViews(viewsets.ModelViewSet):
    queryset = SaleCreditNotes.objects.all()
    serializer_class = SaleCreditNoteSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = create_instance(self, request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class SaleCreditNoteItemsViews(viewsets.ModelViewSet):
    queryset = SaleCreditNoteItems.objects.all()
    serializer_class = SaleCreditNoteItemsSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class SaleDebitNoteViews(viewsets.ModelViewSet):
    queryset = SaleDebitNotes.objects.all()
    serializer_class = SaleDebitNoteSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = create_instance(self, request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class SaleDebitNoteItemsViews(viewsets.ModelViewSet):
    queryset = SaleDebitNoteItems.objects.all()
    serializer_class = SaleDebitNoteItemsSerializers

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        response = create_instance(self, request, *args, **kwargs)
        return response

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

from django.db.models import F

class SaleOrderViewSet(APIView):
    """API ViewSet for handling sale order creation and related data."""
    def get_object(self, pk):
        try:
            return SaleOrder.objects.get(pk=pk)
        except SaleOrder.DoesNotExist:
            logger.warning(f"SaleOrder with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    # def get(self, request, *args, **kwargs):
    #     if "pk" in kwargs:
    #         result = validate_input_pk(self, kwargs['pk'])
    #         return result if result else self.retrieve(self, request, *args, **kwargs)
    #     try:
    #         summary = request.query_params.get("summary", "false").lower() == "true" + "&"
    #         if summary:
    #             logger.info("Retrieving Sale order summary")
    #             saleorders = SaleOrder.objects.all().order_by('-created_at')
    #             data = SaleOrderOptionsSerializer.get_sale_order_summary(saleorders)
    #             return Response(data, status=status.HTTP_200_OK)

    #         logger.info("Retrieving all sale order")

    #         page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
    #         limit = int(request.query_params.get('limit', 10)) 

    #         queryset = SaleOrder.objects.all().order_by('-created_at')

    #         # Apply filters manually
    #         if request.query_params:
    #             filterset = SaleOrderFilter(request.GET, queryset=queryset)
    #             if filterset.is_valid():
    #                 queryset = filterset.qs   

    #         total_count = SaleOrder.objects.count()
        
    #         serializer = SaleOrderOptionsSerializer(queryset, many=True)
    #         logger.info("sale order data retrieved successfully.")
    #         # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
    #         return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    #     except Exception as e:
    #         logger.error(f"An unexpected error occurred: {str(e)}")
    #         return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    # from accounts.models import User  # Import your User model

    # def get(self, request, *args, **kwargs):
    #     if "pk" in kwargs:
    #         result = validate_input_pk(self, kwargs['pk'])
    #         return result if result else self.retrieve(self, request, *args, **kwargs)

    #     try:
    #         # Check if the 'records_all' filter is set in the query params
    #         records_all = request.query_params.get("records_all", "false").lower() == "true"
            
    #         logger.info(f"Fetching records_all: {records_all}")

    #         summary = request.query_params.get("summary", "false").lower() == "true"
    #         if summary:
    #             logger.info("Retrieving Sale order summary")
    #             saleorders = SaleOrder.objects.all().order_by('-created_at')
    #             data = SaleOrderOptionsSerializer.get_sale_order_summary(saleorders)
    #             return Response(data, status=status.HTTP_200_OK)

    #         logger.info("Retrieving all sale orders")

    #         page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
    #         limit = int(request.query_params.get('limit', 10))

    #         # Apply filters manually based on the 'records_all' parameter
    #         queryset = SaleOrder.objects.all().order_by('-created_at')

    #         # If records_all is true, fetch records from both mstcnl and devcnl databases
    #         if records_all:
    #             logger.info("Fetching sale orders from both mstcnl and devcnl databases")
    #             # Add logic to combine records from both databases
    #             saleorders_mstcnl = SaleOrder.objects.using('mstcnl').all().order_by('-created_at')
    #             saleorders_devcnl = SaleOrder.objects.using('devcnl').all().order_by('-created_at')
    #             queryset = saleorders_mstcnl | saleorders_devcnl  # Union of both queries

    #         else:
    #             logger.info("Fetching sale orders only from devcnl")
    #             queryset = SaleOrder.objects.using('devcnl').all().order_by('-created_at')

    #         # Apply other filters from SaleOrderFilter
    #         if request.query_params:
    #             filterset = SaleOrderFilter(request.GET, queryset=queryset)
    #             if filterset.is_valid():
    #                 queryset = filterset.qs

    #         total_count = queryset.count()

    #         # Serialize the queryset
    #         serializer = SaleOrderOptionsSerializer(queryset, many=True)

    #         logger.info("Sale order data retrieved successfully.")
    #         return filter_response(queryset.count(), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

    #     except Exception as e:
    #         logger.error(f"Error retrieving sale orders: {str(e)}")
    #         return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def get(self, request, *args, **kwargs):
        """Handles GET requests to retrieve sale orders with optional filters and reports."""
        try:
            if "pk" in kwargs:
                result = validate_input_pk(self, kwargs['pk'])
                return result if result else self.retrieve(self, request, *args, **kwargs)

            if request.query_params.get("summary", "false").lower() == "true" :
                return self.get_summary_data(request)
            
            if request.query_params.get("records_all", "false").lower() == "true" :
                return self.get_summary_data(request)
            
            if request.query_params.get("sales_order_report", "false").lower() == "true" :
                return self.get_sales_order_report(request)
            
            if request.query_params.get("sales_invoice_report", "false").lower() == "true" :
                return self.get_sales_invoice_report(request)
            
            if request.query_params.get("sales_by_product", "false").lower() == "true":
                return self.get_sales_by_product(request)
            
            if request.query_params.get("sales_by_customer", "false").lower() == "true":
                return self.get_sales_by_customer(request)
            
            if request.query_params.get("outstanding_sales_by_customer", "false").lower() == "true":
                return self.get_outstanding_sales_by_customer(request)
            
            if request.query_params.get("sales_tax_report", "false").lower() == "true":
                return self.get_sales_tax_by_product_report(request)
            
            if request.query_params.get("salesperson_performance_report", "false").lower() == "true":
                return self.get_salesperson_performance_report(request)
            
            if request.query_params.get("profit_margin_report", "false").lower() == "true":
                return self.get_profit_margin_report(request)

            return self.get_sale_orders(request)

        except Exception as e:
            logger.error(f"Error retrieving sale orders: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)



    def get_pagination_params(self, request):
        """Extracts pagination parameters from the request."""
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        return page, limit
    
    def get_sale_orders(self, request):
        """Applies filters, pagination, and retrieves sale orders."""
        logger.info("Retrieving all sale orders")

        page, limit = self.get_pagination_params(request)
        
        queryset = SaleOrder.objects.all().order_by('-created_at')

        if request.query_params:
            filterset = SaleOrderFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = SaleOrder.objects.count()
        serializer = SaleOrderSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    # def get_summary_data(self, request):
    #     """Fetches sale order summary data."""
    #     logger.info("Retrieving Sale order summary")

    #     page, limit = self.get_pagination_params(request)
    #     queryset = SaleOrder.objects.all().order_by('-created_at')
        
    #     if request.query_params:
    #         filterset = SaleOrderFilter(request.GET, queryset=queryset)
    #         if filterset.is_valid():
    #             queryset = filterset.qs
                
    #     total_count = SaleOrder.objects.count()
    #     # queryset, total_count = self.apply_filters(request, queryset, SaleOrderFilter, SaleOrder)

    #     serializer = SaleOrderOptionsSerializer(queryset, many=True)
    #     return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
    
    def get_summary_data(self, request):
        """Fetches sale order summary data."""
        logger.info("Retrieving Sale order summary")

        page, limit = self.get_pagination_params(request)
        records_all = request.query_params.get("records_all", "false").lower() == "true"

        if records_all:
            logger.info("Fetching sale order summary from both mstcnl and default databases")
            
            saleorders_mstcnl = SaleOrder.objects.using('mstcnl').all().order_by('-created_at')
            saleorders_devcnl = SaleOrder.objects.using('default').all().order_by('-created_at')
            
            combined_queryset = list(chain(saleorders_mstcnl, saleorders_devcnl))
            total_count = len(combined_queryset)

            start_index = (page - 1) * limit
            end_index = start_index + limit
            paginated_results = combined_queryset[start_index:end_index]

            serializer = SaleOrderOptionsSerializer(paginated_results, many=True)
            return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

        else:
            logger.info("Fetching sale order summary only from default database")
            queryset = SaleOrder.objects.all().order_by('-created_at')
            
            if request.query_params:
                filterset = SaleOrderFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs

            total_count = queryset.count()
            paginated_results = queryset[(page - 1) * limit: page * limit]

            serializer = SaleOrderOptionsSerializer(paginated_results, many=True)
            return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)
    
    def get_sales_order_report(self, request):
        """Fetches sales order details with required fields."""
        logger.info("Retrieving sales order report data")
        page, limit = self.get_pagination_params(request)

        # Group the necessary fields from SaleOrder model.
        queryset = SaleOrder.objects.all().order_by('-created_at')

        if request.query_params:
            filterset = SalesOrderReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
                
        total_count = SaleOrder.objects.count()
        serializer = SalesOrderReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    def get_sales_invoice_report(self, request):
        """Fetches detailed sales invoice report data."""
        logger.info("Retrieving detailed sales invoice report data")
        page, limit = self.get_pagination_params(request)

        # Retrieve full SaleInvoiceOrders model instances.
        queryset = SaleInvoiceOrders.objects.all().order_by('-invoice_date')
        
        if request.query_params:
            filterset = SalesInvoiceReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
                
        total_count = SaleInvoiceOrders.objects.count()
        serializer = SalesInvoiceReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)


    def get_sales_by_product(self, request):
        """Fetches total sales amount grouped by product."""
        logger.info("Retrieving sales by product data")
        page, limit = self.get_pagination_params(request)
        
        # queryset = SaleOrderItems.objects.values(product=F('product_id__name'),total_sales=F('amount')).order_by('-total_sales')

        # queryset = SaleOrderItems.objects.values(product=F('product_id__name')).annotate(
        #     total_sales=Sum('amount', output_field=models.DecimalField())  
        # ).order_by('-total_sales')
        
        queryset = SaleOrderItems.objects.values( "product_id__name").annotate(
                total_quantity_sold=Sum("quantity"),
                total_sales=Sum("amount"),
            ).order_by('-total_sales')

        # if request.query_params:
        #     filterset = SalesByProductReportFilter(request.GET, queryset=queryset)
        #     if filterset.is_valid():
        #         queryset = filterset.qs
                
        # total_count = queryset.count()
        if request.query_params:
            filterset = SalesByProductReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
                
        total_count = queryset.count()
        serializer = SalesByProductReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
    
    def get_sales_by_customer(self, request):
        """Fetches total sales amount grouped by customer."""
        logger.info("Retrieving sales by customer data")
        page, limit = self.get_pagination_params(request)

        queryset = SaleOrder.objects.values(customer=F('customer_id__name')).annotate(
            total_sales=Sum('item_value', output_field=models.DecimalField())  # Ensure DecimalField output
        ).order_by('-total_sales')

        if request.query_params:
            filterset = SalesByCustomerReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = queryset.count()
        serializer = SalesByCustomerSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
    
    
    def get_outstanding_sales_by_customer(self, request):
        """Fetches pending payments grouped by customer."""
        logger.info("Retrieving outstanding sales (pending payments) by customer data")
        page, limit = self.get_pagination_params(request)

        # Annotate each invoice with total_paid and pending_amount,
        # Group by customer: sum total_amount and sum payments made.
        queryset = SaleInvoiceOrders.objects.filter(
            total_amount__gt=F('payment_transactions__amount')
        ).values(customer=F('customer_id__name')).annotate(
            total_invoice=Sum('total_amount', output_field=models.DecimalField()),
            total_paid=Coalesce(
                Sum('payment_transactions__amount', filter=Q(payment_transactions__payment_status='Completed'),
                    output_field=models.DecimalField()),
                Value(0),
                output_field=models.DecimalField()
            )
        ).annotate(
            total_pending=F('total_invoice') - F('total_paid')
        ).filter(total_pending__gt=0).order_by('-total_pending')

        if request.query_params:
            filterset = OutstandingSalesReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = queryset.count()
        serializer = OutstandingSalesSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    def get_sales_tax_by_product_report(self, request):
        """Fetches sales tax report data grouped by product and GST type."""
        logger.info("Retrieving sales tax by product report data")
        page, limit = self.get_pagination_params(request)
        
        # Group by product and GST type, then aggregate total sales and tax.
        queryset = SaleInvoiceItems.objects.values(
            'product_id__name',
            'sale_invoice_id__gst_type_id__name'
        ).annotate(
            product=F('product_id__name'),
            gst_type=F('sale_invoice_id__gst_type_id__name'),
            total_sales=Sum('amount', output_field=DecimalField(max_digits=18, decimal_places=2)),
            total_tax=Sum('tax', output_field=DecimalField(max_digits=18, decimal_places=2))
        ).order_by('-total_tax')
        
        # Calculate total count before applying filters
        total_count = queryset.count()
        
        # Apply optional filters if provided
        if request.query_params:
            filterset = SalesTaxByProductReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
        
        # Manual pagination if needed
        if not hasattr(filterset, 'page_number') and not hasattr(filterset, 'limit'):
            start_index = (page - 1) * limit
            end_index = start_index + limit
            queryset = queryset[start_index:end_index]
                    
        serializer = SalesTaxByProductReportSerializer(queryset, many=True)
        return filter_response(queryset.count(), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

    def get_salesperson_performance_report(self, request):
        """Fetches sales figures aggregated per salesperson."""
        logger.info("Retrieving salesperson performance report data")
        page, limit = self.get_pagination_params(request)
        
        # Group invoices by salesperson (using the related field from order_salesman_id)
        queryset = SaleInvoiceOrders.objects.values(
            salesperson=F('order_salesman_id__name')  # Assumes OrdersSalesman model has a 'name' field.
        ).annotate(
            total_sales=Sum('total_amount', output_field=DecimalField(max_digits=18, decimal_places=2))
        ).order_by('-total_sales')
        
        # Optional filtering if query parameters are provided.
        if request.query_params:
            filterset = SalespersonPerformanceReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = queryset.count()
        serializer = SalespersonPerformanceReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
    
    
    def get_profit_margin_report(self, request):
        """Fetches profit margin analysis on sold products."""
        logger.info("Retrieving profit margin report data")
        page, limit = self.get_pagination_params(request)
        
        # Aggregate total sales and total cost by product.
        queryset = SaleOrderItems.objects.values(
            product=F('product_id__name')
        ).annotate(
            total_sales=Sum('amount'),
            total_quantity=Sum('quantity'),
            total_cost=Sum(
                ExpressionWrapper(
                    F('product_id__purchase_rate') * F('quantity'),
                    output_field=DecimalField(max_digits=18, decimal_places=2)
                )
            )
        )
        
        # Annotate profit and profit margin.
        # Profit = total_sales - total_cost
        # Profit Margin = (profit / total_sales) * 100
        queryset = queryset.annotate(
            profit=ExpressionWrapper(F('total_sales') - F('total_cost'), output_field=DecimalField(max_digits=18, decimal_places=2))
        ).annotate(
            profit_margin=ExpressionWrapper(
                (F('profit') / F('total_sales')) * 100,
                output_field=DecimalField(max_digits=5, decimal_places=2)
            )
        ).order_by('-profit_margin')
        
        if request.query_params:
            filterset = ProfitMarginReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
        
        total_count = queryset.count()
        serializer = ProfitMarginReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a sale order and its related data (items, attachments, and shipments) from mstcnl or devcnl database.
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Step 1: Try to fetch from mstcnl
            try:
                sale_order = SaleOrder.objects.using('mstcnl').get(pk=pk)
                using_db = 'mstcnl'
                logger.info(f"Sale order found in 'mstcnl' database with pk: {pk}")
            except SaleOrder.DoesNotExist:
                # Step 2: If not found in mstcnl, try devcnl (default)
                try:
                    sale_order = SaleOrder.objects.using('default').get(pk=pk)
                    using_db = 'default'
                    logger.info(f"Sale order found in 'devcnl' database with pk: {pk}")
                except SaleOrder.DoesNotExist:
                    # Step 3: Not found anywhere
                    logger.error(f"Sale order with pk {pk} does not exist in any database.")
                    return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

            # Step 4: Serialize the sale order
            sale_order_serializer = SaleOrderSerializer(sale_order)

            # Step 5: Fetch related data using correct database
            items_data = self.get_related_data(SaleOrderItems, SaleOrderItemsSerializer, 'sale_order_id', pk, using_db)
            attachments_data = self.get_related_data(OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk, using_db)
            shipments_data = self.get_related_data(OrderShipments, OrderShipmentsSerializer, 'order_id', pk, using_db)
            shipments_data = shipments_data[0] if len(shipments_data) > 0 else {}

            custom_field_values_data = self.get_related_data(CustomFieldValue, CustomFieldValueSerializer, 'custom_id', pk, using_db)

            custom_data = {
                "sale_order": sale_order_serializer.data,
                "sale_order_items": items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data,
                "custom_field_values": custom_field_values_data
            }

            logger.info("Sale order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Exception as e:
            logger.exception(f"An error occurred while retrieving sale order with pk {pk}: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_related_data(self, model, serializer_class, filter_field, filter_value, using_db='default'):
        """
        Retrieves related data for a given model, serializer, and filter field from specified database.
        """
        try:
            related_data = model.objects.using(using_db).filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug(f"Retrieved related data for model {model.__name__} with filter {filter_field}={filter_value} from {using_db}.")
            return serializer.data
        except Exception as e:
            logger.exception(f"Error retrieving related data for model {model.__name__} with filter {filter_field}={filter_value} from {using_db}: {str(e)}")
            return []


    # @transaction.atomic
    # def delete(self, request, pk, *args, **kwargs):
    #     """
    #     Handles the deletion of a sale order and its related attachments and shipments.
    #     """
    #     try:
    #         # Get the SaleOrder instance
    #         instance = SaleOrder.objects.get(pk=pk)

    #         # Delete related OrderAttachments and OrderShipments
    #         if not delete_multi_instance(pk, SaleOrder, OrderAttachments, main_model_field_name='order_id'):
    #             return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         if not delete_multi_instance(pk, SaleOrder, OrderShipments, main_model_field_name='order_id'):
    #             return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         if not delete_multi_instance(pk, SaleOrder, CustomFieldValue, main_model_field_name='custom_id'):
    #             return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    #         # Delete the main SaleOrder instance
    #         instance.delete()

    #         logger.info(f"SaleOrder with ID {pk} deleted successfully.")
    #         return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
    #     except SaleOrder.DoesNotExist:
    #         logger.warning(f"SaleOrder with ID {pk} does not exist.")
    #         return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         logger.error(f"Error deleting SaleOrder with ID {pk}: {str(e)}")
    #         return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale order and its related attachments and shipments.
        Based on the sale_order_id, it checks the appropriate database and deletes the records.
        """
        db_to_use = None
        try:
            # Check which database the SaleOrder belongs to
            SaleOrder.objects.using('mstcnl').get(sale_order_id=pk)
            set_db('mstcnl')
            db_to_use = 'mstcnl'
        except SaleOrder.DoesNotExist:
            try:
                SaleOrder.objects.using('default').get(sale_order_id=pk)
                set_db('default')
                db_to_use = 'default'
            except SaleOrder.DoesNotExist:
                logger.warning(f"SaleOrder with ID {pk} does not exist in any database.")
                return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

        try:
            # Get the SaleOrder instance from the appropriate database
            instance = SaleOrder.objects.using(db_to_use).get(pk=pk)

            # Delete related OrderAttachments, OrderShipments, and CustomFieldValues from the correct database
            if not delete_multi_instance(pk, SaleOrder, OrderAttachments, main_model_field_name='order_id', using_db=db_to_use):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not delete_multi_instance(pk, SaleOrder, OrderShipments, main_model_field_name='order_id', using_db=db_to_use):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not delete_multi_instance(pk, SaleOrder, CustomFieldValue, main_model_field_name='custom_id', using_db=db_to_use):
                return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main SaleOrder instance from the correct database
            instance.delete(using=db_to_use)

            logger.info(f"SaleOrder with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)

        except SaleOrder.DoesNotExist:
            logger.warning(f"SaleOrder with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleOrder with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    @transaction.atomic
    # def create(self, request, *args, **kwargs):
    #     # Extracting data from the request
    #     given_data = request.data

    #     # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
    #     sale_order_data = given_data.pop('sale_order', None)
    #     if sale_order_data:
    #         order_error = validate_payload_data(self, sale_order_data, SaleOrderSerializer)
    #         validate_order_type(sale_order_data, order_error, OrderTypes, look_up='order_type')

    #     sale_order_items_data = given_data.pop('sale_order_items', None)
    #     if sale_order_items_data:
    #         item_error = validate_multiple_data(self, sale_order_items_data, SaleOrderItemsSerializer, ['sale_order_id'])

    #     order_attachments_data = given_data.pop('order_attachments', None)
    #     if order_attachments_data:
    #         attachment_error = validate_multiple_data(self, order_attachments_data, OrderAttachmentsSerializer, ['order_id', 'order_type_id'])
    #     else:
    #         attachment_error = []

    #     order_shipments_data = given_data.pop('order_shipments', None)
    #     if len(order_shipments_data) > 1:
    #         shipments_error = validate_multiple_data(self, [order_shipments_data], OrderShipmentsSerializer, ['order_id', 'order_type_id'])
    #     else:
    #         shipments_error = []
    #         order_shipments_data = {}

    #     custom_fields_data = given_data.pop('custom_field_values', None)
    #     if custom_fields_data:
    #         custom_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'])
    #     else:
    #         custom_error = []

    #     # Ensure mandatory data is present
    #     if not sale_order_data or not sale_order_items_data:
    #         logger.error("Sale order and sale order items are mandatory but not provided.")
    #         return build_response(0, "Sale order and sale order items are mandatory", [], status.HTTP_400_BAD_REQUEST)

    #     errors = {}
    #     if order_error:
    #         errors["sale_order"] = order_error
    #     if item_error:
    #         errors["sale_order_items"] = item_error
    #     if attachment_error:
    #         errors['order_attachments'] = attachment_error
    #     if shipments_error:
    #         errors['order_shipments'] = shipments_error
    #     if custom_error:
    #         errors['custom_field_values'] = custom_error
    #     if errors:
    #         return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

    #     # ---------------------- D A T A   C R E A T I O N ----------------------------#
    #     sale_type_id = sale_order_data.get('sale_type_id')
    #     print("--------- Views -----------")
    #     print("sale_type_id : ", sale_type_id)
    #     sale_type_val = None
    #     if sale_type_id:
    #         try:
    #             sale_type_obj = SaleTypes.objects.get(sale_type_id=sale_type_id)
    #             sale_type_val = sale_type_obj.name
    #         except SaleTypes.DoesNotExist:
    #             sale_type_val = None

    #     is_other_sale = sale_type_val == 'Other'
    #     # Step 2: Decide the DB
    #     if is_other_sale:
    #         set_db('mstcnl')
    #         using_db = 'mstcnl'
    #     else:
    #         set_db('default')
    #         using_db = 'default'
    #     print("using_db : ", using_db)
    #     # Step 3: Create SaleOrder Data
    #     new_sale_order_data = generic_data_creation(self, [sale_order_data], SaleOrderSerializer, using=using_db)
    #     new_sale_order_data = new_sale_order_data[0]
    #     sale_order_id = new_sale_order_data.get("sale_order_id", None)
    #     logger.info(f'SaleOrder - created in {using_db} DB')

    #     # Step 4: Create SaleOrderItems Data
    #     if sale_order_id:
    #         update_fields = {'sale_order_id': sale_order_id}
    #         items_data = generic_data_creation(self, sale_order_items_data, SaleOrderItemsSerializer, update_fields, using=using_db)
    #         logger.info(f'SaleOrderItems - created in {using_db} DB')
            
    #     # Get order_type_id from OrderTypes model
    #     order_type_val = sale_order_data.get('order_type')
    #     order_type = get_object_or_none(OrderTypes, name=order_type_val)
    #     type_id = order_type.order_type_id

    #     # Create OrderAttachments Data in 'mstcnl' DB
    #     update_fields = {'order_id': sale_order_id, 'order_type_id': type_id}
    #     if order_attachments_data:
    #         order_attachments = generic_data_creation(self, order_attachments_data, OrderAttachmentsSerializer, update_fields, using=using_db)
    #         logger.info('OrderAttachments - created in mstcnl DB')
    #     else:
    #         # Since OrderAttchments Data is optional, so making it as an empty data list
    #         order_attachments = []

    #     # Create OrderShipments Data in 'mstcnl' DB
    #     if order_shipments_data:
    #         order_shipments = generic_data_creation(self, [order_shipments_data], OrderShipmentsSerializer, update_fields, using=using_db)
    #         logger.info('OrderShipments - created in mstcnl DB')
    #     else:
    #         # Since OrderAttchments Data is optional, so making it as an empty data list
    #         order_shipments = []

    #     # Create CustomFieldValues Data in 'mstcnl' DB
    #     if custom_fields_data:
    #         update_fields = {'custom_id': sale_order_id}
    #         custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, update_fields, using=using_db)
    #         logger.info('CustomFieldValues - created in mstcnl DB')

    #     # -------------------- Inventory Blocking ----------------------------------------------
    #     if sale_order_data.get("sale_estimate", "").lower() != "yes":
    #         block_duration = InventoryBlockConfig.objects.filter(product_id__isnull=True).first()
    #         block_duration_hours = getattr(block_duration, 'block_duration_hours', 24)
    #         expiration_time = timezone.now() + timedelta(hours=block_duration_hours)

    #         blocked_inventory_data = []
    #         for item in sale_order_items_data:
    #             product_id = item.get("product_id")
    #             ordered_qty = item.get("quantity")

    #             product = Products.objects.filter(product_id=product_id).first()
    #             if product:
    #                 if product.balance >= ordered_qty:
    #                     product.balance = F('balance') - ordered_qty
    #                     product.save(update_fields=['balance'])

    #                 blocked_inventory_data.append(BlockedInventory(
    #                     sale_order_id=SaleOrder.objects.get(sale_order_id=sale_order_id),
    #                     product_id=Products.objects.get(product_id=product_id),
    #                     blocked_qty=ordered_qty,
    #                     expiration_time=expiration_time
    #                 ))
    #             else:
    #                 return build_response(0, f"Product with ID {product_id} not found.", [], status.HTTP_404_NOT_FOUND)

    #         BlockedInventory.objects.bulk_create(blocked_inventory_data, ignore_conflicts=True)
    #         logger.info("Inventory blocked for sale order %s.", sale_order_id)

    #     # ---------------------- R E S P O N S E ----------------------------#
    #     custom_data = {
    #         "sale_order": new_sale_order_data,
    #         "sale_order_items": items_data,
    #         "order_attachments": order_attachments,
    #         "order_shipments": order_shipments,
    #         "custom_field_values": custom_fields_data
    #     }
    #     return build_response(1, "Sale Order created successfully", custom_data, status.HTTP_201_CREATED)


    def create(self, request, *args, **kwargs):
        given_data = request.data

        # Determine DB before any validation
        sale_type_id = given_data.get('sale_order', {}).get('sale_type_id')
        sale_type_val = None
        if sale_type_id:
            try:
                sale_type_obj = SaleTypes.objects.get(sale_type_id=sale_type_id)
                sale_type_val = sale_type_obj.name
            except SaleTypes.DoesNotExist:
                sale_type_val = None

        is_other_sale = sale_type_val == 'Other'
        using_db = 'mstcnl' if is_other_sale else 'default'
        set_db(using_db)
        print("using_db : ", using_db)

        # Extract payload after DB is known
        sale_order_data = given_data.pop('sale_order', None)
        sale_order_items_data = given_data.pop('sale_order_items', None)
        order_attachments_data = given_data.pop('order_attachments', None)
        order_shipments_data = given_data.pop('order_shipments', None)
        custom_fields_data = given_data.pop('custom_field_values', None)

        # ---------------------- VALIDATION ----------------------------------#
        order_error, item_error, attachment_error, shipments_error, custom_error = [], [], [], [], []

        if sale_order_data:
            order_error = validate_payload_data(self, sale_order_data, SaleOrderSerializer, using=using_db)
            validate_order_type(sale_order_data, order_error, OrderTypes, look_up='order_type', using=using_db)

        if sale_order_items_data:
            item_error = validate_multiple_data(self, sale_order_items_data, SaleOrderItemsSerializer, ['sale_order_id'], using=using_db)

        if order_attachments_data:
            attachment_error = validate_multiple_data(self, order_attachments_data, OrderAttachmentsSerializer, ['order_id', 'order_type_id'], using=using_db)

        if order_shipments_data:
            if len(order_shipments_data) > 1:
                shipments_error = validate_multiple_data(self, [order_shipments_data], OrderShipmentsSerializer, ['order_id', 'order_type_id'], using=using_db)
            else:
                order_shipments_data = {}
                shipments_error = []

        if custom_fields_data:
            custom_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'], using=using_db)

        if not sale_order_data or not sale_order_items_data:
            logger.error("Sale order and sale order items are mandatory but not provided.")
            return build_response(0, "Sale order and sale order items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error: errors["sale_order"] = order_error
        if item_error: errors["sale_order_items"] = item_error
        if attachment_error: errors["order_attachments"] = attachment_error
        if shipments_error: errors["order_shipments"] = shipments_error
        if custom_error: errors["custom_field_values"] = custom_error

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        new_sale_order_data = generic_data_creation(self, [sale_order_data], SaleOrderSerializer, using=using_db)[0]
        sale_order_id = new_sale_order_data.get("sale_order_id", None)
        logger.info(f'SaleOrder - created in {using_db} DB')

        if sale_order_id:
            update_fields = {'sale_order_id': sale_order_id}
            items_data = generic_data_creation(self, sale_order_items_data, SaleOrderItemsSerializer, update_fields, using=using_db)
            logger.info(f'SaleOrderItems - created in {using_db} DB')

        order_type_val = sale_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val, using=using_db)
        type_id = order_type.order_type_id

        update_fields = {'order_id': sale_order_id, 'order_type_id': type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(self, order_attachments_data, OrderAttachmentsSerializer, update_fields, using=using_db)
            logger.info(f'OrderAttachments - created in {using_db} DB')
        else:
            order_attachments = []

        if order_shipments_data:
            order_shipments = generic_data_creation(self, [order_shipments_data], OrderShipmentsSerializer, update_fields, using=using_db)
            logger.info(f'OrderShipments - created in {using_db} DB')
        else:
            order_shipments = []

        if custom_fields_data:
            update_fields = {'custom_id': sale_order_id}
            custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, update_fields, using=using_db)
            logger.info(f'CustomFieldValues - created in {using_db} DB')

        # -------------------- Inventory Blocking ----------------------------------
        if sale_order_data.get("sale_estimate", "").lower() != "yes":
            block_duration = InventoryBlockConfig.objects.using(using_db).filter(product_id__isnull=True).first()
            block_duration_hours = getattr(block_duration, 'block_duration_hours', 24)
            expiration_time = timezone.now() + timedelta(hours=block_duration_hours)

            blocked_inventory_data = []
            for item in sale_order_items_data:
                product_id = item.get("product_id")
                ordered_qty = item.get("quantity")
                product = Products.objects.using(using_db).filter(product_id=product_id).first()

                if product:
                    if product.balance >= ordered_qty:
                        product.balance = F('balance') - ordered_qty
                        product.save(using=using_db, update_fields=['balance'])

                    blocked_inventory_data.append(BlockedInventory(
                        sale_order_id=SaleOrder.objects.using(using_db).get(sale_order_id=sale_order_id),
                        product_id=Products.objects.using(using_db).get(product_id=product_id),
                        blocked_qty=ordered_qty,
                        expiration_time=expiration_time
                    ))
                else:
                    return build_response(0, f"Product with ID {product_id} not found.", [], status.HTTP_404_NOT_FOUND)

            BlockedInventory.objects.using(using_db).bulk_create(blocked_inventory_data, ignore_conflicts=True)
            logger.info("Inventory blocked for sale order %s.", sale_order_id)

        # ---------------------- R E S P O N S E ----------------------------#
        custom_data = {
            "sale_order": new_sale_order_data,
            "sale_order_items": items_data,
            "order_attachments": order_attachments,
            "order_shipments": order_shipments,
            "custom_field_values": custom_fields_data
        }
        return build_response(1, "Sale Order created successfully", custom_data, status.HTTP_201_CREATED)


    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        # ----------------------------------- C H E C K  D A T A B A S E -----------------------------#
        db_to_use = None
        try:
            # Check if sale_order_id exists in the mstcnl database
            SaleOrder.objects.using('mstcnl').get(sale_order_id=pk)
            set_db('mstcnl')
            db_to_use = 'mstcnl'
        except ObjectDoesNotExist:
            try:
                # Check if sale_order_id exists in the devcnl database
                SaleOrder.objects.using('default').get(sale_order_id=pk)
                set_db('default')
                db_to_use = 'default'
            except ObjectDoesNotExist:
                logger.error(f"Sale order with id {pk} not found in any database.")
                return build_response(0, f"Sale order with id {pk} not found", [], status.HTTP_404_NOT_FOUND)

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        given_data = request.data

        # Validate SaleOrder Data
        sale_order_data = given_data.pop('sale_order', None)
        if sale_order_data:
            sale_order_data['sale_order_id'] = pk
            # Validate SaleOrder Data
            order_error = validate_multiple_data(
                self, [sale_order_data], SaleOrderSerializer, ['order_no'], using_db=db_to_use
            )

            validate_order_type(sale_order_data, order_error, OrderTypes, look_up='order_type')

        # Validate SaleOrderItems Data
        sale_order_items_data = given_data.pop('sale_order_items', None)
        if sale_order_items_data:
            exclude_fields = ['sale_order_id']
            item_error = validate_put_method_data(
                self, sale_order_items_data, SaleOrderItemsSerializer,
                exclude_fields, SaleOrderItems, current_model_pk_field='sale_order_item_id', db_to_use=db_to_use
            )

        # Validate OrderAttachments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id', 'order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(
                self, order_attachments_data, OrderAttachmentsSerializer,
                exclude_fields, OrderAttachments, current_model_pk_field='attachment_id', db_to_use=db_to_use
            )
        else:
            attachment_error = []

        # Validate OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(
                self, order_shipments_data, OrderShipmentsSerializer,
                exclude_fields, OrderShipments, current_model_pk_field='shipment_id', db_to_use=db_to_use
            )
        else:
            shipments_error = []

        # Validate CustomFieldValues Data
        custom_field_values_data = given_data.pop('custom_field_values', None)
        if custom_field_values_data:
            exclude_fields = ['custom_id']
            custom_field_values_error = validate_put_method_data(
                self, custom_field_values_data, CustomFieldValueSerializer,
                exclude_fields, CustomFieldValue, current_model_pk_field='custom_field_value_id', db_to_use=db_to_use
            )
        else:
            custom_field_values_error = []

        # Ensure mandatory data is present
        if not sale_order_data or not sale_order_items_data:
            logger.error("Sale order and sale order items are mandatory but not provided.")
            return build_response(0, "Sale order and sale order items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["sale_order"] = order_error
        if item_error:
            errors["sale_order_items"] = item_error
        if attachment_error:
            errors["order_attachments"] = attachment_error
        if shipments_error:
            errors["order_shipments"] = shipments_error
        if custom_field_values_error:
            errors["custom_field_values"] = custom_field_values_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T E -----------------------------------------#

        # Update SaleOrder
        if sale_order_data:
            update_fields = []
            saleorder_data = update_multi_instances(
                self, pk, [sale_order_data], SaleOrder, SaleOrderSerializer,
                update_fields, main_model_related_field='sale_order_id',
                current_model_pk_field='sale_order_id', using_db=db_to_use
            )

        # Update SaleOrderItems
        update_fields = {'sale_order_id': pk}
        items_data = update_multi_instances(
            self, pk, sale_order_items_data, SaleOrderItems, SaleOrderItemsSerializer,
            update_fields, main_model_related_field='sale_order_id',
            current_model_pk_field='sale_order_item_id', using_db=db_to_use  # Ensuring same DB is used
        )

        # Get order_type_id from OrderTypes model
        order_type_val = sale_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id if order_type else None

        # Update OrderAttachments
        if order_attachments_data:
            update_fields = {'order_id': pk, 'order_type_id': type_id}
            attachment_data = update_multi_instances(
                self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer,
                update_fields, main_model_related_field='order_id',
                current_model_pk_field='attachment_id', using_db=db_to_use
            )
        else:
            attachment_data = []

        # Update OrderShipments
        if order_shipments_data:
            update_fields = {'order_id': pk, 'order_type_id': type_id}
            shipment_data = update_multi_instances(
                self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer,
                update_fields, main_model_related_field='order_id',
                current_model_pk_field='shipment_id', using_db=db_to_use
            )
        else:
            shipment_data = []

        # Update CustomFieldValues
        if custom_field_values_data:
            custom_field_values_data = update_multi_instances(
                self, pk, custom_field_values_data, CustomFieldValue, CustomFieldValueSerializer,
                {}, main_model_related_field='custom_id',
                current_model_pk_field='custom_field_value_id', using_db=db_to_use
            )

        # Prepare custom_data for response
        custom_data = {
            "sale_order": saleorder_data[0] if saleorder_data else {},
            "sale_order_items": items_data if items_data else [],
            "order_attachments": attachment_data if attachment_data else [],
            "order_shipments": shipment_data[0] if shipment_data else {},
            "custom_field_values": custom_field_values_data if custom_field_values_data else []
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

    
    def patch(self, request, pk, format=None):
        sale_order = self.get_object(pk)
        if not sale_order:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        flow_status_id = request.data.get("flow_status_id")
        order_status_id = request.data.get("order_status_id")

        if flow_status_id:
            try:
                new_flow_status = FlowStatus.objects.get(pk=flow_status_id)
                sale_order.flow_status_id = new_flow_status
            except FlowStatus.DoesNotExist:
                return build_response(0, "Invalid flow_status_id", [], status.HTTP_400_BAD_REQUEST)
            
        if order_status_id:
            try:
                new_order_status = OrderStatuses.objects.get(pk=order_status_id)
                sale_order.order_status_id = new_order_status
            except OrderStatuses.DoesNotExist:
                return build_response(0, "Invalid order_status_id", [], status.HTTP_400_BAD_REQUEST)

        serializer = SaleOrderOptionsSerializer(sale_order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return build_response(1, 'Data Updated Successfully', serializer.data, status.HTTP_200_OK)
        
        return build_response(0, 'Data not updated', [], status.HTTP_400_BAD_REQUEST)

#-------------------- Sale Order End ----------------------------------------------------    


class SaleInvoiceOrdersViewSet(APIView):
    """
    API ViewSet for handling sale invoice order creation and related data.
    """

    def get_object(self, pk):
        try:
            return SaleInvoiceOrders.objects.get(pk=pk)
        except SaleInvoiceOrders.DoesNotExist:
            logger.warning(f"SaleInvoiceOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result =  validate_input_pk(self,kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs) 
        try:
            # Check if the 'records_all' filter is set in the query params
            records_all = request.query_params.get("records_all", "false").lower() == "true"
            
            logger.info(f"Fetching records_all: {records_all}")
            
            summary = request.query_params.get("summary", "false").lower() == "true" + "&"
            if summary:
                logger.info("Retrieving sale invoice order summary")
                saleinvoiceorder = SaleInvoiceOrders.objects.all().order_by('-created_at')
                data = SaleInvoiceOrderOptionsSerializer.get_sale_invoice_order_summary(saleinvoiceorder)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
             
            logger.info("Retrieving all sale invoice orders")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 

            queryset = SaleInvoiceOrders.objects.all().order_by('-created_at')

            # If records_all is true, fetch records from both mstcnl and devcnl databases
            if records_all:
                logger.info("Fetching sale Invoice orders from both mstcnl and devcnl databases")
                
                # Query the 'mstcnl' database
                saleinvoiceorders_mstcnl = SaleInvoiceOrders.objects.using('mstcnl').all().order_by('-created_at')
                # Query the 'devcnl' database
                saleinvoiceorders_devcnl = SaleInvoiceOrders.objects.using('default').all().order_by('-created_at')

                # Combine the two querysets
                combined_queryset = list(chain(saleinvoiceorders_mstcnl, saleinvoiceorders_devcnl))

                # We need to paginate the combined result manually since it's from multiple databases
                total_count = len(combined_queryset)
                start_index = (page - 1) * limit
                end_index = start_index + limit
                paginated_results = combined_queryset[start_index:end_index]
            else:
                logger.info("Fetching sale orders only from devcnl")
                # Only query from the 'devcnl' database
                queryset = SaleInvoiceOrders.objects.using('default').all().order_by('-created_at')
                # Apply filters manually
                if request.query_params:
                    filterset = SaleInvoiceOrdersFilter(request.GET, queryset=queryset)
                    if filterset.is_valid():
                        queryset = filterset.qs 
                        
                total_count = queryset.count()
                paginated_results = queryset[(page - 1) * limit: page * limit]

            # total_count = SaleInvoiceOrders.objects.count()

            serializer = SaleInvoiceOrderOptionsSerializer(paginated_results, many=True)
            logger.info("sale order invoice data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(total_count,"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a sale invoice order and its related data (items, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Step 1: Try to fetch from mstcnl
            try:
                sale_invoice_order = SaleInvoiceOrders.objects.using('mstcnl').get(pk=pk)
                using_db = 'mstcnl'
                logger.info(f"SaleInvoiceOrders found in 'mstcnl' database with pk: {pk}")
            except SaleInvoiceOrders.DoesNotExist:
                # Step 2: If not found in mstcnl, try devcnl (default)
                try:
                    sale_invoice_order = SaleInvoiceOrders.objects.using('default').get(pk=pk)
                    using_db = 'default'
                    logger.info(f"SaleInvoiceOrders found in 'devcnl' database with pk: {pk}")
                except SaleInvoiceOrders.DoesNotExist:
                    # Step 3: Not found anywhere
                    logger.error(f"SaleInvoiceOrders with pk {pk} does not exist in any database.")
                    return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

            # Retrieve the SaleInvoiceOrders instance
            #sale_invoice_order = get_object_or_404(SaleInvoiceOrders, pk=pk)
            sale_invoice_order_serializer = SaleInvoiceOrdersSerializer(sale_invoice_order)

            # Retrieve related data
            items_data = self.get_related_data(SaleInvoiceItems, SaleInvoiceItemsSerializer, 'sale_invoice_id', pk, using_db)
            attachments_data = self.get_related_data(OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk, using_db)
            shipments_data = self.get_related_data(OrderShipments, OrderShipmentsSerializer, 'order_id', pk, using_db)
            shipments_data = shipments_data[0] if len(shipments_data)>0 else {}
            
            # Retrieve custom field values
            custom_field_values_data = self.get_related_data(CustomFieldValue, CustomFieldValueSerializer, 'custom_id', pk, using_db)

            # Customizing the response data
            custom_data = {
                "sale_invoice_order": sale_invoice_order_serializer.data,
                "sale_invoice_items": items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data,
                "custom_field_values": custom_field_values_data
            }
            logger.info("Sale invoice order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Sale invoice order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving sale invoice order with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_related_data(self, model, serializer_class, filter_field, filter_value, using_db='default'):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.using(using_db).filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.", model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s", model.__name__, filter_field, filter_value, str(e))
            return []

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale invoice order and its related attachments and shipments.
        """
        db_to_use = None
        try:
            # Check which database the SaleInvoiceOrders belongs to
            SaleInvoiceOrders.objects.using('mstcnl').get(sale_invoice_id=pk)
            set_db('mstcnl')
            db_to_use = 'mstcnl'
        except SaleInvoiceOrders.DoesNotExist:
            try:
                SaleInvoiceOrders.objects.using('default').get(sale_invoice_id=pk)
                set_db('default')
                db_to_use = 'default'
            except SaleInvoiceOrders.DoesNotExist:
                logger.warning(f"Sale Invoice Orders with ID {pk} does not exist in any database.")
                return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        try:
            # Get the SaleInvoiceOrders instance
            instance = SaleInvoiceOrders.objects.using(db_to_use).get(pk=pk)

            # Delete related OrderAttachments and OrderShipments
            if not delete_multi_instance(pk, SaleInvoiceOrders, OrderAttachments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, SaleInvoiceOrders, OrderShipments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, SaleInvoiceOrders, CustomFieldValue, main_model_field_name='custom_id'):
                return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main SaleInvoiceOrder instance from the correct database
            instance.delete(using=db_to_use)

            logger.info(f"SaleInvoiceOrders with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except SaleInvoiceOrders.DoesNotExist:
            logger.warning(f"SaleInvoiceOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleInvoiceOrders with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Extracting data from the request
        given_data = request.data
        
        # Set default DB (important before validations)
        using_db = 'default'

        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """

        # Validate SaleInvoiceOrders Data
        sale_invoice_order_data = given_data.pop('sale_invoice_order', None)  # parent_data
        if sale_invoice_order_data:
            order_error = validate_payload_data(self, sale_invoice_order_data, SaleInvoiceOrdersSerializer)
            # validate the order_type in 'sale_invoice_order_data' data
            validate_order_type(sale_invoice_order_data, order_error, OrderTypes, look_up='order_type')

        # Validate SaleInvoiceItems Data
        sale_invoice_items_data = given_data.pop('sale_invoice_items', None)
        if sale_invoice_items_data:
            item_error = validate_multiple_data(self, sale_invoice_items_data, SaleInvoiceItemsSerializer, ['sale_invoice_id'])

        # Validate OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(self, order_attachments_data, OrderAttachmentsSerializer, ['order_id', 'order_type_id'])
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Validate OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_multiple_data(self, [order_shipments_data], OrderShipmentsSerializer, ['order_id', 'order_type_id'])
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []
            
        # Validate Custom Fields Data
        custom_fields_data = given_data.pop('custom_field_values', None)
        if custom_fields_data:
            custom_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'])
        else:
            custom_error = []

        # Ensure mandatory data is present
        if not sale_invoice_order_data or not sale_invoice_items_data:
            logger.error(
                "Sale invoice order and sale invoice items are mandatory but not provided.")
            return build_response(0, "Sale invoice order and sale invoice items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["sale_invoice_order"] = order_error
        if item_error:
            errors["sale_invoice_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if custom_error:
            errors['custom_field_values'] = custom_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # Stock verification
        stock_error = product_stock_verification(Products, ProductVariation, sale_invoice_items_data)
        if stock_error:
            return build_response(0, f"ValidationError :", stock_error, status.HTTP_400_BAD_REQUEST)          

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """
        bill_type = sale_invoice_order_data.get('bill_type')

        bill_type_obj = None
        if bill_type:
            try:
                bill_type_obj = 'Others'
            except SaleTypes.DoesNotExist:
                bill_type_obj = None

        is_other_sale = bill_type_obj == 'Others'
        # Step 2: Decide the DB
        if is_other_sale:
            set_db('mstcnl')
            using_db = 'mstcnl'
        else:
            set_db('default')
            using_db = 'default'
        # Hence the data is validated , further it can be created.

        # Create SaleInvoiceOrders Data
        new_sale_invoice_order_data = generic_data_creation(self, [sale_invoice_order_data], SaleInvoiceOrdersSerializer, using=using_db)
        new_sale_invoice_order_data = new_sale_invoice_order_data[0]
        sale_invoice_id = new_sale_invoice_order_data.get("sale_invoice_id", None)  # Fetch sale_invoice_id from mew instance
        logger.info('SaleInvoiceOrders - created in {using_db} DB')

        # Create SaleInvoiceItems Data
        update_fields = {'sale_invoice_id': sale_invoice_id}
        items_data = generic_data_creation(self, sale_invoice_items_data, SaleInvoiceItemsSerializer, update_fields, using=using_db)
        logger.info('SaleInvoiceItems - created in {using_db} DB')

        # Get order_type_id from OrderTypes model
        order_type_val = sale_invoice_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id': sale_invoice_id, 'order_type_id': type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(self, order_attachments_data, OrderAttachmentsSerializer, update_fields, using=using_db)
            logger.info('OrderAttchments - created*')
        else:
            # Since OrderAttchments Data is optional, so making it as an empty data list
            order_attachments = []

        # create OrderShipments Data
        if order_shipments_data:
            order_shipments = generic_data_creation(self, [order_shipments_data], OrderShipmentsSerializer, update_fields, using=using_db)
            order_shipments = order_shipments[0]
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = {}
            
        # Assign `custom_id = sale_inovice_id` for CustomFieldValues
        if custom_fields_data:
            update_fields = {'custom_id': sale_invoice_id}  # Now using `custom_id` like `order_id`
            custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, update_fields, using=using_db)
            logger.info('CustomFieldValues - created*')
        else:
            custom_fields_data = []

        # Update Product Stock
        update_product_stock(Products, ProductVariation, sale_invoice_items_data, 'subtract')

        custom_data = {
            "sale_invoice_order": new_sale_invoice_order_data,
            "sale_invoice_items": items_data,
            "order_attachments": order_attachments,
            "order_shipments": order_shipments,
            "custom_field_values": custom_fields_data
        }

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        # ----------------------------------- C H E C K  D A T A B A S E -----------------------------#
        db_to_use = None
        try:
            # Check if sale_invoice_id exists in the mstcnl database
            SaleInvoiceOrders.objects.using('mstcnl').get(sale_invoice_id=pk)
            set_db('mstcnl')
            db_to_use = 'mstcnl'
        except ObjectDoesNotExist:
            try:
                # Check if sale_invoice_id exists in the devcnl database
                SaleInvoiceOrders.objects.using('default').get(sale_invoice_id=pk)
                set_db('default')
                db_to_use = 'default'
            except ObjectDoesNotExist:
                logger.error(f"Sale Invoice Order with id {pk} not found in any database.")
                return build_response(0, f"Sale Invoice order with id {pk} not found", [], status.HTTP_404_NOT_FOUND)

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Validated SaleInvoiceOrders Data
        sale_invoice_order_data = given_data.pop('sale_invoice_order', None)  # parent_data
        if sale_invoice_order_data:
            sale_invoice_order_data['sale_invoice_id'] = pk
            order_error = validate_multiple_data(self, [sale_invoice_order_data], SaleInvoiceOrdersSerializer, ['invoice_no'], using_db=db_to_use)
            # validate the 'order_type' in 'sale_invoice_order' data
            validate_order_type(sale_invoice_order_data, order_error, OrderTypes, look_up='order_type')

        # Vlidated SaleInvoiceItems Data
        sale_invoice_items_data = given_data.pop('sale_invoice_items', None)
        if sale_invoice_items_data:
            exclude_fields = ['sale_invoice_id']
            item_error = validate_put_method_data(self, sale_invoice_items_data, SaleInvoiceItemsSerializer, exclude_fields, SaleInvoiceItems, current_model_pk_field='sale_invoice_item_id', db_to_use=db_to_use)

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id', 'order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id', db_to_use=db_to_use)
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id', db_to_use=db_to_use)
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []
            
        # Validated CustomFieldValues Data
        custom_field_values_data = given_data.pop('custom_field_values', None)
        if custom_field_values_data:
            exclude_fields = ['custom_id']
            custom_field_values_error = validate_put_method_data(self, custom_field_values_data, CustomFieldValueSerializer, exclude_fields, CustomFieldValue, current_model_pk_field='custom_field_value_id', db_to_use=db_to_use)
        else:
            custom_field_values_error = []

        # Ensure mandatory data is present
        if not sale_invoice_order_data or not sale_invoice_items_data:
            logger.error("Sale invoice order and sale invoice items are mandatory but not provided.")
            return build_response(0, "Sale order and sale order items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["sale_invoice_order"] = order_error
        if item_error:
            errors["sale_invoice_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if custom_field_values_error:
            errors['custom_field_values'] = custom_field_values_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update SaleInvoiceOrders
        if sale_invoice_order_data:
            update_fields = []  # No need to update any fields
            saleinvoice_order_data = update_multi_instances(self, pk, sale_invoice_order_data, SaleInvoiceOrders, SaleInvoiceOrdersSerializer, update_fields, main_model_related_field='sale_invoice_id', current_model_pk_field='sale_invoice_id', using_db=db_to_use)
            saleinvoice_order_data = saleinvoice_order_data[0] if len(saleinvoice_order_data)==1 else saleinvoice_order_data

        # Update the 'sale_order_items'
        update_fields = {'sale_invoice_id': pk}
        invoice_items_data = update_multi_instances(self, pk, sale_invoice_items_data, SaleInvoiceItems, SaleInvoiceItemsSerializer, update_fields, main_model_related_field='sale_invoice_id', current_model_pk_field='sale_invoice_item_id', using_db=db_to_use)

        # Get 'order_type_id' from 'OrderTypes' model
        order_type_val = sale_invoice_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id': pk, 'order_type_id': type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id', using_db=db_to_use)

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id', using_db=db_to_use)
        shipment_data = shipment_data[0] if len(shipment_data)==1 else shipment_data
        
        # Update CustomFieldValues Data
        if custom_field_values_data:
            custom_field_values_data = update_multi_instances(self, pk, custom_field_values_data, CustomFieldValue, CustomFieldValueSerializer, {}, main_model_related_field='custom_id', current_model_pk_field='custom_field_value_id', using_db=db_to_use)
        

        custom_data = {
            "sale_invoice_order": saleinvoice_order_data,
            "sale_invoice_items": invoice_items_data if invoice_items_data else [],
            "order_attachments": attachment_data if attachment_data else [],
            "order_shipments": shipment_data if shipment_data else {},
            "custom_field_values": custom_field_values_data if custom_field_values_data else []  # Add custom field values to response
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

class SaleReturnOrdersViewSet(APIView):
    def get_object(self, pk):
        try:
            return SaleReturnOrders.objects.get(pk=pk)
        except SaleReturnOrders.DoesNotExist:
            logger.warning(f"SaleReturnOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result =  validate_input_pk(self,kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs) 
        try:
            summary = request.query_params.get("summary", "false").lower() == "true" + "&"
            if summary:
                logger.info("Retrieving sale return orders summary")
                salereturnorders = SaleReturnOrders.objects.all().order_by('-created_at')
                data = SaleReturnOrdersOptionsSerializer.get_sale_return_orders_summary(salereturnorders)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
             
            logger.info("Retrieving all sale return order")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            
            queryset = SaleReturnOrders.objects.all().order_by('-created_at')

            # Apply filters manually
            if request.query_params:
                filterset = SaleReturnOrdersFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            total_count = SaleReturnOrders.objects.count()

            serializer = SaleReturnOrdersOptionsSerializer(queryset, many=True)
            logger.info("sale return order data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a sale return order and its related data (items, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleReturnOrders instance
            sale_return_order = get_object_or_404(SaleReturnOrders, pk=pk)
            sale_return_order_serializer = SaleReturnOrdersSerializer(sale_return_order)

            # Retrieve related data
            items_data = self.get_related_data(
                SaleReturnItems, SaleReturnItemsSerializer, 'sale_return_id', pk)
            attachments_data = self.get_related_data(
                OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk)
            shipments_data = self.get_related_data(
                OrderShipments, OrderShipmentsSerializer, 'order_id', pk)
            shipments_data = shipments_data[0] if len(shipments_data)>0 else {}
            
            # Retrieve custom field values
            custom_field_values_data = self.get_related_data(CustomFieldValue, CustomFieldValueSerializer, 'custom_id', pk)

            # Customizing the response data
            custom_data = {
                "sale_return_order": sale_return_order_serializer.data,
                "sale_return_items": items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data,
                "custom_field_values": custom_field_values_data
            }
            logger.info("Sale return order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Sale return order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving sale return order with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale return order and its related attachments and shipments.
        """
        try:
            # Get the SaleReturnOrders instance
            instance = SaleReturnOrders.objects.get(pk=pk)

            # Delete related OrderAttachments and OrderShipments
            if not delete_multi_instance(pk, SaleReturnOrders, OrderAttachments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, SaleReturnOrders, OrderShipments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, SaleReturnOrders, CustomFieldValue, main_model_field_name='custom_id'):
                return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main SaleOrder instance
            instance.delete()

            logger.info(f"SaleReturnOrders with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except SaleReturnOrders.DoesNotExist:
            logger.warning(f"SaleReturnOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleReturnOrder with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Extracting data from the request
        given_data = request.data

        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """

        # Vlidated SaleReturnOrders Data
        sale_return_order_data = given_data.pop('sale_return_order', None)  # parent_data
        if sale_return_order_data:
            order_error = validate_payload_data(
                self, sale_return_order_data, SaleReturnOrdersSerializer)
            # validate the order_type in 'sale_return_order' data
            validate_order_type(sale_return_order_data, order_error,
                                OrderTypes, look_up='order_type')

        # Vlidated SaleReturnItems Data
        sale_return_items_data = given_data.pop('sale_return_items', None)
        if sale_return_items_data:
            item_error = validate_multiple_data(
                self, sale_return_items_data, SaleReturnItemsSerializer, ['sale_return_id'])

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(
                self, order_attachments_data, OrderAttachmentsSerializer, ['order_id', 'order_type_id'])
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_multiple_data(
                self, [order_shipments_data], OrderShipmentsSerializer, ['order_id', 'order_type_id'])
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []
            
        # Validate Custom Fields Data
        custom_fields_data = given_data.pop('custom_field_values', None)
        if custom_fields_data:
            custom_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'])
        else:
            custom_error = []

        # Ensure mandatory data is present
        if not sale_return_order_data or not sale_return_items_data:
            logger.error(
                "Sale return order and sale return items are mandatory but not provided.")
            return build_response(0, "Sale return order and sale return items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["sale_return_order"] = order_error
        if item_error:
            errors["sale_return_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if custom_error:
            errors['custom_field_values'] = custom_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create SaleReturnOrders Data
        new_sale_return_order_data = generic_data_creation(self, [sale_return_order_data], SaleReturnOrdersSerializer)
        new_sale_return_order_data = new_sale_return_order_data[0]
        sale_return_id = new_sale_return_order_data.get("sale_return_id", None)  # Fetch sale_return_id from mew instance
        logger.info('SaleReturnOrders - created*')

        # Create SaleReturnItems Data
        update_fields = {'sale_return_id': sale_return_id}
        items_data = generic_data_creation(
            self, sale_return_items_data, SaleReturnItemsSerializer, update_fields)
        logger.info('SaleReturnItems - created*')

        # Get order_type_id from OrderTypes model
        order_type_val = sale_return_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id': sale_return_id, 'order_type_id': type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(
                self, order_attachments_data, OrderAttachmentsSerializer, update_fields)
            logger.info('OrderAttchments - created*')
        else:
            # Since OrderAttchments Data is optional, so making it as an empty data list
            order_attachments = []

        # create OrderShipments Data
        if order_shipments_data:
            order_shipments = generic_data_creation(
                self, [order_shipments_data], OrderShipmentsSerializer, update_fields)
            order_shipments = order_shipments[0]
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = {}
            
        # Assign `custom_id = vendor_id` for CustomFieldValues
        if custom_fields_data:
            update_fields = {'custom_id': sale_return_id}  # Now using `custom_id` like `order_id`
            custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, update_fields)
            logger.info('CustomFieldValues - created*')
        else:
            custom_fields_data = []

        # Update the stock with returned products.
        update_product_stock(Products, ProductVariation, sale_return_items_data, 'add')

        custom_data = {
            "sale_return_order": new_sale_return_order_data,
            "sale_return_items": items_data,
            "order_attachments": order_attachments,
            "order_shipments": order_shipments,
            "custom_field_values": custom_fields_data
        }

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Vlidated SaleReturnOrders Data
        sale_return_order_data = given_data.pop('sale_return_order', None)  # parent_data
        if sale_return_order_data:
            sale_return_order_data['sale_return_id'] = pk
            order_error = validate_multiple_data(self, [sale_return_order_data], SaleReturnOrdersSerializer, ['return_no'])
            # validate the order_type in 'sale_return_order' data
            validate_order_type(sale_return_order_data, order_error,OrderTypes, look_up='order_type')

        # Vlidated SaleReturnItems Data
        sale_return_items_data = given_data.pop('sale_return_items', None)
        if sale_return_items_data:
            exclude_fields = ['sale_return_id']
            item_error = validate_put_method_data(self, sale_return_items_data, SaleReturnItemsSerializer,
                                                  exclude_fields, SaleReturnItems, current_model_pk_field='sale_order_item_id')

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id', 'order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []
            
        # Validated CustomFieldValues Data
        custom_field_values_data = given_data.pop('custom_field_values', None)
        if custom_field_values_data:
            exclude_fields = ['custom_id']
            custom_field_values_error = validate_put_method_data(self, custom_field_values_data, CustomFieldValueSerializer, exclude_fields, CustomFieldValue, current_model_pk_field='custom_field_value_id')
        else:
            custom_field_values_error = []

        # Ensure mandatory data is present
        if not sale_return_order_data or not sale_return_items_data:
            logger.error(
                "Sale return order and sale return items are mandatory but not provided.")
            return build_response(0, "Sale return order and sale return items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["sale_return_order"] = order_error
        if item_error:
            errors["sale_return_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if custom_field_values_error:
            errors['custom_field_values'] = custom_field_values_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update SaleReturnOrders
        if sale_return_order_data:
            update_fields = []  # No need to update any fields
            return_order_data = update_multi_instances(self, pk, sale_return_order_data, SaleReturnOrders, SaleReturnOrdersSerializer,update_fields, main_model_related_field='sale_return_id', current_model_pk_field='sale_return_id')
            return_order_data = return_order_data[0] if len(return_order_data)==1 else return_order_data

        # Update the 'sale_return_items'
        update_fields = {'sale_return_id': pk}
        items_data = update_multi_instances(self, pk, sale_return_items_data, SaleReturnItems, SaleReturnItemsSerializer,
                                            update_fields, main_model_related_field='sale_return_id', current_model_pk_field='sale_return_item_id')

        # Get 'order_type_id' from 'OrderTypes' model
        order_type_val = sale_return_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id': pk, 'order_type_id': type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id')

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id')
        
        # Update CustomFieldValues Data
        if custom_field_values_data:
            custom_field_values_data = update_multi_instances(self, pk, custom_field_values_data, CustomFieldValue, CustomFieldValueSerializer, {}, main_model_related_field='custom_id', current_model_pk_field='custom_field_value_id')

        custom_data = {
            "sale_return_order": return_order_data,
            "sale_return_items": items_data if items_data else [],
            "order_attachments": attachment_data if attachment_data else [],
            "order_shipments": shipment_data if shipment_data else {},
            "custom_field_values": custom_field_values_data if custom_field_values_data else []  # Add custom field values to response
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

class QuickPackCreateViewSet(APIView):
    """
    API ViewSet for handling Quick_Packs creation and related data.
    """
    def get_object(self, pk):
        try:
            return QuickPacks.objects.get(pk=pk)
        except QuickPacks.DoesNotExist:
            logger.warning(f"QuickPacks with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    # Get DB Objects
    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result =  validate_input_pk(self,kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs) 
        try:
            logger.info("Retrieving all QuickPacks")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10))   

            queryset = QuickPacks.objects.all().order_by('-created_at')	

            # Apply filters manually
            if request.query_params:
                filterset = QuickPacksFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            total_count = QuickPacks.objects.count()
                     
            serializer = QuickPackSerializer(queryset, many=True)
            logger.info("QuickPacks data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a QuickPacks and its related data (items).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleOrder instance
            quick_packs = get_object_or_404(QuickPacks, pk=pk)
            quick_packs_serializer = QuickPackSerializer(quick_packs)

            # Retrieve related data
            items_data = self.get_related_data(
                QuickPackItems, QuickPackItemSerializer, 'quick_pack_id', pk)
            
            # Customizing the response data
            custom_data = {
                "quick_pack_data": quick_packs_serializer.data,
                "quick_pack_data_items": items_data,                  
            }

            logger.info("quick_packs and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("quick_packs with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving quick_packs with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a Quick Packs.
        """
        try:
            # Get the QuickPacks instance
            instance = QuickPacks.objects.get(pk=pk)

           # Delete the main QuickPacks instance
            '''
            All related instances will be deleted when parent record is deleted. all child models have foreignkey relation with parent table
            '''
            instance.delete()

            logger.info(f"QuickPacks with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except QuickPacks.DoesNotExist:
            logger.warning(f"QuickPacks with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting QuickPacks with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        # Extracting data from the request
        given_data = request.data

        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """

        # Vlidated quick_packs_data
        quick_packs_data = given_data.pop('quick_pack_data', None)  # parent_data
        if quick_packs_data:
            quick_packs_error = validate_payload_data(
                self, quick_packs_data, QuickPackSerializer)

        # Vlidated quick_pack_data_items Data
        quick_pack_items_data = given_data.pop('quick_pack_data_items', None)
        if quick_pack_items_data:
            item_error = validate_multiple_data(
                self, quick_pack_items_data, QuickPackItemSerializer, ['quick_pack_id'])

        # Ensure mandatory data is present
        if not quick_packs_data or not quick_pack_items_data:
            logger.error("Quick Packs and Quick Pack Items items are mandatory but not provided.")
            return build_response(0, "Quick Packs and Quick Pack items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if quick_packs_error:
            errors["quick_pack_data"] = quick_packs_error
        if item_error:
            errors["quick_pack_data_items"] = item_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """
        # Hence the data is validated , further it can be created.

        # Create quick_pack Data
        new_quick_pack_data = generic_data_creation(self, [quick_packs_data], QuickPackSerializer)
        new_quick_pack_data = new_quick_pack_data[0]
        quick_pack_id = new_quick_pack_data.get("quick_pack_id", None)  # Fetch quick_pack_id from mew instance
        logger.info('quick_pack - created*')

        # Create QuickPackItem Data
        update_fields = {'quick_pack_id': quick_pack_id}
        items_data = generic_data_creation(
            self, quick_pack_items_data, QuickPackItemSerializer, update_fields)
        logger.info('QuickPackItem - created*')

        custom_data = {
            "quick_pack_data": new_quick_pack_data,
            "quick_pack_data_items": items_data,            
        }

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    def put(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
         # Get the given data from request
        given_data = request.data
 
        # Vlidated Vendor Data
        quick_pack_data = given_data.pop('quick_pack_data', None)
        if quick_pack_data:
            order_error = validate_payload_data(self, quick_pack_data , QuickPackSerializer)

        # Vlidated QuickPackItems Data
        quick_pack_data_items = given_data.pop('quick_pack_data_items', None)
        if quick_pack_data_items:
            exclude_fields = ['quick_pack_id']
            item_error = validate_put_method_data(self, quick_pack_data_items, QuickPackItemSerializer,
                                    exclude_fields, QuickPackItems, current_model_pk_field='quick_pack_item_id')

      # Ensure mandatory data is present
        if not quick_pack_data or not quick_pack_data_items:
            logger.error("quick_pack and sale quick_pack_items are mandatory but not provided.")
            return build_response(0, "quick_pack and quick_pack_items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if order_error:
            errors["quick_pack"] = order_error
        if item_error:
            errors["quick_pack_items"] = item_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update QuickPacks
        if quick_pack_data:
            update_fields = []  # No need to update any fields
            quickpack_data = update_multi_instances(self, pk, quick_pack_data, QuickPacks, QuickPackSerializer,
                                                    update_fields, main_model_related_field='quick_pack_id', current_model_pk_field='quick_pack_id')

        # Update the 'QuickPackItems'
        update_fields = {'quick_pack_id': pk}
        items_data = update_multi_instances(self, pk, quick_pack_data_items, QuickPackItems, QuickPackItemSerializer,
                                            update_fields, main_model_related_field='quick_pack_id', current_model_pk_field='quick_pack_item_id')

        custom_data = [
            {"quick_pack_data": quickpack_data},
            {"quick_pack_data_items": items_data if items_data else []}           
        ]

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

class SaleReceiptCreateViewSet(APIView):
    """
    API ViewSet for handling Lead creation and related data.
    """

    def get_object(self, pk):
        try:
            return SaleReceipt.objects.get(pk=pk)
        except SaleReceipt.DoesNotExist:
            logger.warning(f"SaleReceipt with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all sale_receipt")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 

            queryset = SaleReceipt.objects.all().order_by('-created_at')	

            # Apply filters manually
            if request.query_params:
                filterset = SaleReceiptFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            total_count = SaleInvoiceOrders.objects.count()

            serializer = SaleReceiptSerializer(queryset, many=True)
            logger.info("sale_receipt data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a sale_receipt and its related data (assignment_history, and Interaction).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleReceipt instance
            sale_receipt = get_object_or_404(SaleReceipt, pk=pk)
            sale_receipt_serializer = SaleReceiptSerializer(sale_receipt)


            # Customizing the response data
            custom_data = {
                "sale_receipt": sale_receipt_serializer.data
                }
            logger.info("sale_receipt and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Lead record with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving sale_receipt with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale_receipt and its related assignments and interactions.
        """
        try:
            # Get the SaleReceipt instance
            instance = SaleReceipt.objects.get(pk=pk)

            # Delete the main SaleReceipt instance
            '''
            All related instances will be deleted when parent record is deleted. all child models have foreignkey relation with parent table
            '''
            instance.delete()

            logger.info(f"SaleReceipt with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except SaleReceipt.DoesNotExist:
            logger.warning(f"SaleReceipt with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleReceipt with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Extracting data from the request
        given_data = request.data

        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """

        # Validate SaleReceipt Data
        sale_receipt_data = given_data.pop('sale_receipt', None)  # parent_data
        if sale_receipt_data:
            sale_receipt_error = validate_payload_data(self, sale_receipt_data, SaleReceiptSerializer)

        # Ensure mandatory data is present
        if not sale_receipt_data:
            logger.error("Sale Receipt data is mandatory but not provided.")
            return build_response(0, "Sale Receipt data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if sale_receipt_error:
            errors["sale_receipt"] = sale_receipt_error

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create SaleReceipt Data
        new_sale_receipt_data = generic_data_creation(self, [sale_receipt_data], SaleReceiptSerializer)
        new_sale_receipt_data = new_sale_receipt_data[0]
        sale_receipt_id = new_sale_receipt_data.get("sale_receipt_id", None)  # Fetch sale_receipt_id from mew instance
        logger.info('SaleReceipt - created*')

        #create History for Lead with assignemnt date as current and leave the end date as null.
        update_fields = {'sale_receipt_id':sale_receipt_id}

        return build_response(1, "Record created successfully", {
            'sale_receipt': new_sale_receipt_data
        }, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Vlidated SaleOrder Data
        sale_receipt_data = given_data.pop('sale_receipt', None)  # parent_data
        if sale_receipt_data:
            sale_receipt_data['sale_receipt_id'] = pk
            sale_receipt_error = validate_multiple_data(self, [sale_receipt_data], SaleReceiptSerializer, [])

        if sale_receipt_error:
            return build_response(0, "ValidationError", sale_receipt_error, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update SaleOrder
        if sale_receipt_data:
            update_fields = []  # No need to update any fields
            saleorder_data = update_multi_instances(self, pk, [sale_receipt_data], SaleReceipt, SaleReceiptSerializer,
                                                    update_fields, main_model_related_field='sale_receipt_id', current_model_pk_field='sale_receipt_id')

        custom_data = {
            "sale_receipt": saleorder_data[0] if saleorder_data else {}
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

class WorkflowCreateViewSet(APIView):
    """
    API ViewSet for handling workflow creation and related data.
    """

    def get_object(self, pk):
        try:
            return Workflow.objects.get(pk=pk)
        except Workflow.DoesNotExist:
            logger.warning(f"Workflow with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            return self.retrieve(request, *args, **kwargs)
        try:
            logger.info("Retrieving all workflows")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10))

            queryset = Workflow.objects.all().order_by('-created_at')

            # Apply filters manually
            if request.query_params:
                filterset = WorkflowFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            total_count = Workflow.objects.count()

            serializer = WorkflowSerializer(queryset, many=True)
            logger.info("Workflow data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a workflow and its related workflow stages.
        """
        pk = kwargs.get('pk')
        if not pk:
            logger.error("Primary key not provided in request.")
            return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

        try:
            # Retrieve the Workflow instance
            workflow = get_object_or_404(Workflow, pk=pk)
            workflow_serializer = WorkflowSerializer(workflow)

            # Retrieve associated workflow stages
            workflow_stages = WorkflowStage.objects.filter(workflow_id=pk)
            workflow_stages_serializer = WorkflowStageSerializer(workflow_stages, many=True)

            # Customizing the response data
            custom_data = {
                "workflow": workflow_serializer.data,
                "workflow_stages": workflow_stages_serializer.data,
            }
            logger.info("Workflow and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        except Http404:
            logger.error(f"Workflow with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(f"An error occurred while retrieving workflow with ID {pk}: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a workflow and its related workflow stages.
        """
        try:
            # Get the Workflow instance
            instance = Workflow.objects.get(pk=pk)
            instance.delete()

            logger.info(f"Workflow with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except Workflow.DoesNotExist:
            logger.warning(f"Workflow with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting Workflow with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        given_data = request.data

        # Extract and validate workflow data if provided
        workflow_data = given_data.get('workflow')
        workflow_instance = None

        if workflow_data:
            # Create a new workflow instance
            workflow_serializer = WorkflowSerializer(data=workflow_data)
            if not workflow_serializer.is_valid():
                return build_response(0, "ValidationError", workflow_serializer.errors, status.HTTP_400_BAD_REQUEST)
            
            # Save the workflow instance
            workflow_instance = workflow_serializer.save()

        if not workflow_instance:
            return build_response(0, "Workflow data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        # Handle workflow stages data
        workflow_stage_data_list = given_data.get('workflow_stages')
        workflow_stage_instances = []

        if workflow_stage_data_list and isinstance(workflow_stage_data_list, list):
            for stage_data in workflow_stage_data_list:
                # Assign the newly created workflow's ID to each stage
                stage_data['workflow_id'] = workflow_instance.pk

                # Validate and save the workflow stage
                workflow_stage_serializer = WorkflowStageSerializer(data=stage_data)
                if not workflow_stage_serializer.is_valid():
                    return build_response(0, "ValidationError", workflow_stage_serializer.errors, status.HTTP_400_BAD_REQUEST)
                
                # Save the stage instance
                stage_instance = workflow_stage_serializer.save()
                workflow_stage_instances.append(stage_instance)

        # Prepare response data
        workflow_data_response = WorkflowSerializer(workflow_instance).data
        workflow_stage_data_response = WorkflowStageSerializer(workflow_stage_instances, many=True).data

        return build_response(1, "Record created successfully", {
            'workflow': workflow_data_response,
            'workflow_stages': workflow_stage_data_response
        }, status.HTTP_201_CREATED)


    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        given_data = request.data
        errors = {}

        # Update the Workflow data
        workflow_data = given_data.get('workflow')
        if workflow_data:
            try:
                workflow_instance = Workflow.objects.get(pk=pk)
                workflow_serializer = WorkflowSerializer(workflow_instance, data=workflow_data, partial=True)
                if not workflow_serializer.is_valid():
                    errors["workflow"] = workflow_serializer.errors
                else:
                    workflow_serializer.save()
            except Workflow.DoesNotExist:
                return build_response(0, f"Workflow with ID {pk} does not exist.", [], status.HTTP_404_NOT_FOUND)

        # Handle Workflow Stages
        workflow_stage_data_list = given_data.get('workflow_stages')
        existing_stage_ids = set()

        if workflow_stage_data_list and isinstance(workflow_stage_data_list, list):
            for stage_data in workflow_stage_data_list:
                stage_id = stage_data.get('workflow_stage_id')
                if stage_id:
                    # Update the existing workflow stage by ID
                    try:
                        stage_instance = WorkflowStage.objects.get(pk=stage_id, workflow_id=pk)
                        stage_serializer = WorkflowStageSerializer(stage_instance, data=stage_data, partial=True)

                        if not stage_serializer.is_valid():
                            errors[f"workflow_stage_{stage_id}"] = stage_serializer.errors
                        else:
                            stage_serializer.save()
                            existing_stage_ids.add(stage_id)
                    except WorkflowStage.DoesNotExist:
                        return build_response(0, f"WorkflowStage with ID {stage_id} does not exist.", [], status.HTTP_400_BAD_REQUEST)
                else:
                    # Create a new WorkflowStage if not found
                    stage_data['workflow_id'] = pk  # Attach the workflow ID to the new stage data
                    stage_serializer = WorkflowStageSerializer(data=stage_data)

                    if stage_serializer.is_valid():
                        new_stage = stage_serializer.save()
                        existing_stage_ids.add(new_stage.workflow_stage_id)
                    else:
                        errors["workflow_stage_creation"] = stage_serializer.errors

        # Optionally, remove stages that were not included in the update request
        WorkflowStage.objects.filter(workflow_id=pk).exclude(workflow_stage_id__in=existing_stage_ids).delete()

        if errors:
            return build_response(0, "ValidationError", errors, status.HTTP_400_BAD_REQUEST)

        # Prepare the response data
        workflow_data_response = WorkflowSerializer(Workflow.objects.get(pk=pk)).data
        workflow_stage_data_response = WorkflowStageSerializer(
            WorkflowStage.objects.filter(workflow_id=pk), many=True
        ).data

        return build_response(1, "Records updated successfully", {
            'workflow': workflow_data_response,
            'workflow_stages': workflow_stage_data_response
        }, status.HTTP_200_OK)

class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = WorkflowFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Workflow,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class WorkflowStageViewSet(viewsets.ModelViewSet):
    queryset = WorkflowStage.objects.all()
    serializer_class = WorkflowStageSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class SaleReceiptViewSet(viewsets.ModelViewSet):
    queryset = SaleReceipt.objects.all()
    serializer_class = SaleReceiptSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleReceiptFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
# created new view for this
# class ProgressWorkflowView(APIView):
#     """
#     API view to progress the workflow of a specific SaleOrder to the next stage.
#     This view is used to update the flow_status of a sale order, moving it from one stage to the next within its defined workflow.
#     """

#     def post(self, request, pk, format=None):
#         """
#         Handle POST requests to progress the workflow of the specified SaleOrder.
        
#         Parameters:
#         - request: The HTTP request object.
#         - pk: The primary key of the SaleOrder to be updated.
#         - format: An optional format specifier for content negotiation.

#         Returns:
#         - Custom JSON structure with 'count', 'message', and 'data'.
#         """
#         try:
#             # Attempt to retrieve the SaleOrder by its primary key (pk)
#             sale_order = SaleOrder.objects.get(pk=pk)

#             # Try to progress the workflow to the next stage
#             if sale_order.progress_workflow():
#                 response_data = {
#                     "count": 1,
#                     "message": "Success",
#                     "data": {"status": "Flow status updated successfully."}
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)
#             else:
#                 response_data = {
#                     "count": 1,
#                     "message": "Success",
#                     "data": {"status": "No further stages. Workflow is complete."}
#                 }
#                 return Response(response_data, status=status.HTTP_200_OK)
#         except SaleOrder.DoesNotExist:
#             response_data = {
#                 "count": 0,
#                 "message": "SaleOrder not found.",
#                 "data": None
#             }
#             return Response(response_data, status=status.HTTP_404_NOT_FOUND)
        
class SaleCreditNoteViewset(APIView):
    
    def get_object(self, pk):
        try:
            return SaleCreditNotes.objects.get(pk=pk)
        except SaleCreditNotes.DoesNotExist:
            logger.warning(f"salecreditnote with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        
    def get(self, request, *args, **kwargs):
        print("Hello")
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all salecreditnote")
            print("try block is triggering")
            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10))
            
            queryset = SaleCreditNotes.objects.all().order_by('-created_at')	
            # Apply filters manually
            if request.query_params:
                filterset = SaleCreditNotesFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs  
                    
            total_count = SaleCreditNotes.objects.count()
        
            serializer = SaleCreditNoteSerializers(queryset, many=True)
            logger.info("salecreditnote data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleOrder instance
            sale_credit_note = get_object_or_404(SaleCreditNotes, pk=pk)
            sale_credit_note_serializer = SaleCreditNoteSerializers(sale_credit_note)

            # Retrieve related data
            credit_items_data = self.get_related_data(
                SaleCreditNoteItems, SaleCreditNoteItemsSerializers, 'credit_note_id', pk)

            # Customizing the response data
            custom_data = {
                "sale_credit_note": sale_credit_note_serializer.data,
                "sale_credit_note_items": credit_items_data,
            }
            logger.info("salecreditnote and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("salecreditnote with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving salecreditnote with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []
        
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale order and its related attachments and shipments.
        """
        try:
            # Get the SaleCreditNotes instance
            instance = SaleCreditNotes.objects.get(pk=pk)

            # Delete the main SaleCreditNotes instance
            '''
            All related instances will be deleted when parent record is deleted. all child models have foreignkey relation with parent table
            '''
            instance.delete()

            logger.info(f"SaleCreditNotes with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except SaleCreditNotes.DoesNotExist:
            logger.warning(f"SaleCreditNotes with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleCreditNotes with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("Create is running now:")
        # Extracting data from the request
        given_data = request.data

        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        # Vlidated SaleOrder Data
        sale_credit_note_data = given_data.pop('sale_credit_note', None)  # parent_data
        if sale_credit_note_data:
            credit_note_error = validate_payload_data(
                self, sale_credit_note_data, SaleCreditNoteSerializers)

        # Vlidated SaleOrderItems Data
        sale_credit_items_data = given_data.pop('sale_credit_note_items', None)
        if sale_credit_items_data:
            item_error = validate_multiple_data(
                self, sale_credit_items_data, SaleCreditNoteItemsSerializers, ['credit_note_id'])

        # Ensure mandatory data is present
        if not sale_credit_note_data or not sale_credit_items_data:
            logger.error("SaleCreditNote and SaleCreditNote items are mandatory but not provided.")
            return build_response(0, "SaleCreditNote and SaleCreditNote items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if credit_note_error:
            errors["sale_credit_note"] = credit_note_error
        if item_error:
            errors["sale_credit_note_items"] = item_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create SaleCreditNotes Data
        new_sale_credit_note_data = generic_data_creation(self, [sale_credit_note_data], SaleCreditNoteSerializers)
        new_sale_credit_note_data = new_sale_credit_note_data[0]
        credit_note_id = new_sale_credit_note_data.get("credit_note_id", None)
        logger.info('SaleCreditNotes - created*')

        # Create SaleCreditNotesItems Data
        update_fields = {'credit_note_id': credit_note_id}
        items_data = generic_data_creation(
            self, sale_credit_items_data, SaleCreditNoteItemsSerializers, update_fields)
        logger.info('SaleCreditNotesItems - created*')


        custom_data = {
            "sale_credit_note": new_sale_credit_note_data,
            "sale_credit_note_items": items_data,
        }

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Vlidated SaleOrder Data
        sale_credit_note_data = given_data.pop('sale_credit_note', None)  # parent_data
        if sale_credit_note_data:
            sale_credit_note_data['credit_note_id'] = pk
            credit_note_error = validate_multiple_data(
                self, [sale_credit_note_data], SaleCreditNoteSerializers, ['credit_note_number'])

        # Vlidated SaleOrderItems Data
        sale_credit_items_data = given_data.pop('sale_credit_note_items', None)
        if sale_credit_items_data:
            exclude_fields = ['credit_note_id']
            item_error = validate_put_method_data(self, sale_credit_items_data, SaleCreditNoteItemsSerializers,
                                                  exclude_fields, SaleCreditNoteItems, current_model_pk_field='credit_note_item_id')

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id', 'order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []
            
        # Validated CustomFieldValues Data
        custom_field_values_data = given_data.pop('custom_field_values', None)
        if custom_field_values_data:
            exclude_fields = ['custom_id']
            custom_field_values_error = validate_put_method_data(self, custom_field_values_data, CustomFieldValueSerializer, exclude_fields, CustomFieldValue, current_model_pk_field='custom_field_value_id')
        else:
            custom_field_values_error = []

        # Ensure mandatory data is present
        if not sale_credit_note_data or not sale_credit_items_data:
            logger.error(
                "SaleCreditNote and SaleCreditNote items are mandatory but not provided.")
            return build_response(0, "SaleCreditNote and SaleCreditNote items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if credit_note_error:
            errors["sale_credit_note"] = credit_note_error
        if item_error:
            errors["sale_credit_note_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if custom_field_values_error:
            errors['custom_field_values'] = custom_field_values_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update SaleCreditNotes
        if sale_credit_note_data:
            update_fields = []  # No need to update any fields
            salecreditnote_data = update_multi_instances(self, pk, [sale_credit_note_data], SaleCreditNotes, SaleCreditNoteSerializers,
                                                    update_fields, main_model_related_field='credit_note_id', current_model_pk_field='credit_note_id')

        # Update the 'sale_order_items'
        update_fields = {'credit_note_id': pk}
        items_data = update_multi_instances(self, pk, sale_credit_items_data, SaleCreditNoteItems, SaleCreditNoteItemsSerializers,
                                            update_fields, main_model_related_field='credit_note_id', current_model_pk_field='credit_note_item_id')

        custom_data = {
            "sale_credit_note": salecreditnote_data[0] if salecreditnote_data else {},
            "sale_credit_note_items": items_data if items_data else []
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
    
    def patch(self, request, pk, format=None):
        sale_credit_note = self.get_object(pk)
        if sale_credit_note is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = SaleCreditNoteSerializers(sale_credit_note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SaleDebitNoteViewset(APIView):
    
    def get_object(self, pk):
        try:
            return SaleDebitNotes.objects.get(pk=pk)
        except SaleDebitNotes.DoesNotExist:
            logger.warning(f"salecreditnote with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        
    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all salecreditnote")
            print("try block is triggering")
            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10))
            
            queryset = SaleDebitNotes.objects.all().order_by('-created_at')	
            # Apply filters manually
            if request.query_params:
                filterset = SaleDebitNotesFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs  
                    
            total_count = SaleDebitNotes.objects.count()
        
            serializer = SaleDebitNoteSerializers(queryset, many=True)
            logger.info("salecreditnote data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)


        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def retrieve(self, request, *args, **kwargs):
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleOrder instance
            sale_debit_note = get_object_or_404(SaleDebitNotes, pk=pk)
            sale_debit_note_serializer = SaleDebitNoteSerializers(sale_debit_note)

            # Retrieve related data
            debit_items_data = self.get_related_data(
                SaleDebitNoteItems, SaleDebitNoteItemsSerializers, 'debit_note_id', pk)

            # Customizing the response data
            custom_data = {
                "sale_debit_note": sale_debit_note_serializer.data,
                "sale_debit_note_items": debit_items_data,
            }
            logger.info("salecreditnote and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("salecreditnote with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving salecreditnote with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []
        
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale order and its related attachments and shipments.
        """
        try:
            # Get the SaleDebitNotes instance
            instance = SaleDebitNotes.objects.get(pk=pk)

            # Delete the main SaleDebitNotes instance
            '''
            All related instances will be deleted when parent record is deleted. all child models have foreignkey relation with parent table
            '''
            instance.delete()

            logger.info(f"SaleDebitNotes with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except SaleDebitNotes.DoesNotExist:
            logger.warning(f"SaleDebitNotes with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting SaleDebitNotes with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        print("Create is running now:")
        # Extracting data from the request
        given_data = request.data

        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        # Vlidated SaleOrder Data
        sale_debit_note_data = given_data.pop('sale_debit_note', None)  # parent_data
        if sale_debit_note_data:
            debit_note_error = validate_payload_data(
                self, sale_debit_note_data, SaleDebitNoteSerializers)

        # Vlidated SaleOrderItems Data
        sale_debit_items_data = given_data.pop('sale_debit_note_items', None)
        if sale_debit_items_data:
            item_error = validate_multiple_data(
                self, sale_debit_items_data, SaleDebitNoteItemsSerializers, ['debit_note_id'])

        # Ensure mandatory data is present
        if not sale_debit_note_data or not sale_debit_items_data:
            logger.error("SaleDebitNote and SaleDebitNote items are mandatory but not provided.")
            return build_response(0, "SaleDebitNote and SaleDebitNote items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if debit_note_error:
            errors["sale_debit_note"] = debit_note_error
        if item_error:
            errors["sale_debit_note_items"] = item_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create SaleDebitNotes Data
        new_sale_debit_note_data = generic_data_creation(self, [sale_debit_note_data], SaleDebitNoteSerializers)
        new_sale_debit_note_data = new_sale_debit_note_data[0]
        debit_note_id = new_sale_debit_note_data.get("debit_note_id", None)
        logger.info('SaleDebitNotes - created*')

        # Create SaleCreditNotesItems Data
        update_fields = {'debit_note_id': debit_note_id}
        items_data = generic_data_creation(
            self, sale_debit_items_data, SaleDebitNoteItemsSerializers, update_fields)
        logger.info('SaleCreditNotesItems - created*')


        custom_data = {
            "sale_debit_note": new_sale_debit_note_data,
            "sale_debit_note_items": items_data,
        }

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Vlidated SaleOrder Data
        sale_debit_note_data = given_data.pop('sale_debit_note', None)  # parent_data
        if sale_debit_note_data:
            sale_debit_note_data['debit_note_id'] = pk
            debit_note_error = validate_multiple_data(
                self, [sale_debit_note_data], SaleDebitNoteSerializers, ['debit_note_number'])

        # Vlidated SaleOrderItems Data
        sale_debit_items_data = given_data.pop('sale_debit_note_items', None)
        if sale_debit_items_data:
            exclude_fields = ['debit_note_id']
            item_error = validate_put_method_data(self, sale_debit_items_data, SaleDebitNoteItemsSerializers,
                                                  exclude_fields, SaleDebitNoteItems, current_model_pk_field='debit_note_item_id')

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id', 'order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []
            
        # Validated CustomFieldValues Data
        custom_field_values_data = given_data.pop('custom_field_values', None)
        if custom_field_values_data:
            exclude_fields = ['custom_id']
            custom_field_values_error = validate_put_method_data(self, custom_field_values_data, CustomFieldValueSerializer, exclude_fields, CustomFieldValue, current_model_pk_field='custom_field_value_id')
        else:
            custom_field_values_error = []

        # Ensure mandatory data is present
        if not sale_debit_note_data or not sale_debit_items_data:
            logger.error(
                "SaleDebitNote and SaleDebitNote items are mandatory but not provided.")
            return build_response(0, "SaleDebitNote and SaleDebitNote items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if debit_note_error:
            errors["sale_debit_note"] = debit_note_error
        if item_error:
            errors["sale_debit_note_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if custom_field_values_error:
            errors['custom_field_values'] = custom_field_values_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update SaleDebitNotes
        if sale_debit_note_data:
            update_fields = []  # No need to update any fields
            saledebitnote_data = update_multi_instances(self, pk, [sale_debit_note_data], SaleDebitNotes, SaleDebitNoteSerializers,
                                                    update_fields, main_model_related_field='debit_note_id', current_model_pk_field='debit_note_id')

        # Update the 'sale_order_items'
        update_fields = {'debit_note_id': pk}
        items_data = update_multi_instances(self, pk, sale_debit_items_data, SaleDebitNoteItems, SaleDebitNoteItemsSerializers,
                                            update_fields, main_model_related_field='debit_note_id', current_model_pk_field='debit_note_item_id')

        custom_data = {
            "sale_debit_note": saledebitnote_data[0] if saledebitnote_data else {},
            "sale_debit_note_items": items_data if items_data else []
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
        
    def patch(self, request, pk, format=None):
        sale_debit_note = self.get_object(pk)
        if sale_debit_note is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        
        serializer = SaleDebitNoteSerializers(sale_debit_note, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class MoveToNextStageGenericView(APIView):
    """
    API endpoint to move any module (e.g., Sale Order, Purchase Order, etc.) to the next stage in its workflow.
    It also supports updating specific fields on the object using the PATCH method.
    """

    def post(self, request, module_name, object_id):
        try:
            ModelClass = self.get_model_class(module_name)
            obj = ModelClass.objects.get(pk=object_id)

            # Find the current workflow stage
            current_stage = WorkflowStage.objects.filter(flow_status_id=obj.flow_status_id).first()

            if not current_stage:
                return Response({"error": "Current workflow stage not found."}, status=status.HTTP_404_NOT_FOUND)

            # Check for "Production" stage
            production_stage = WorkflowStage.objects.filter(
                workflow_id=current_stage.workflow_id_id,
                flow_status_id__flow_status_name="Production"
            ).first()

            if current_stage == production_stage:
                # If in "Production", move back to Stage 1
                next_stage = WorkflowStage.objects.filter(
                    workflow_id=current_stage.workflow_id_id,
                    stage_order=1
                ).first()
            else:
                # Otherwise, move to the next stage
                next_stage = WorkflowStage.objects.filter(
                    workflow_id=current_stage.workflow_id_id,
                    stage_order__gt=current_stage.stage_order
                ).order_by('stage_order').first()

            if next_stage:
                obj.flow_status_id = next_stage.flow_status_id
                obj.save()

                return Response({
                    "message": f"{module_name} moved to the next stage.",
                    "current_stage": current_stage.flow_status_id.flow_status_name,
                    "next_stage": next_stage.flow_status_id.flow_status_name
                }, status=status.HTTP_200_OK)

            return Response({"message": f"{module_name} has reached the final stage."}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    def patch(self, request, module_name, object_id):
        """
        Partially update the object's fields, including setting a specific flow status.
        """
        try:
            # Dynamically load the model based on module_name
            ModelClass = self.get_model_class(module_name)
            if not ModelClass:
                return Response({"error": f"Model {module_name} not found."}, status=status.HTTP_404_NOT_FOUND)

            # Fetch the object from the appropriate model
            obj = ModelClass.objects.get(pk=object_id)
            print(f"Updating fields for: {module_name} with ID {object_id}")

            # Update fields with the data from the request
            for field, value in request.data.items():
                if hasattr(obj, field):
                    setattr(obj, field, value)
                    print(f"Updated {field} to {value}")

            # Save the updated object
            obj.save()

            return Response({
                "message": f"{module_name} partially updated successfully.",
                "updated_fields": request.data
            }, status=status.HTTP_200_OK)

        except ModelClass.DoesNotExist:
            return Response({"error": f"{module_name} object with ID {object_id} not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_model_class(self, module_name):
        """
        Helper method to dynamically load the model class.

        Parameters:
            - module_name (str): The name of the model (e.g., 'SaleOrder', 'PurchaseOrder').
        
        Returns:
            - Model class if found, otherwise None.
        """
        try:
            for model in apps.get_models():
                if model.__name__.lower() == module_name.lower():
                    return model
        except LookupError:
            print(f"Model {module_name} not found.")
            return None

class PaymentTransactionAPIView(APIView):
    """
    API endpoint to create a new PaymentTransaction record.
    """
    def post(self, request):
        """
        Handle POST request to create one or more payment transactions by applying the input amount
        across one or more invoices.
        """
        data = request.data
        cust_data = data.get('customer')
        customer_id = cust_data.get('customer_id').replace('-','')
        account_data = data.get('account')
        account_id = account_data.get('account_id').replace('-','')
        description = data.get('description')

        # Validate account_id
        try:
            uuid.UUID(account_id)  # Ensure valid UUID format
            ChartOfAccounts.objects.get(pk=account_id)
        except (ValueError, TypeError, ChartOfAccounts.DoesNotExist) as e:
            return build_response(1, "Invalid account ID format OR Chart Of Account does not exist.", str(e), status.HTTP_404_NOT_FOUND)

        # Validate customer_id
        try:
            uuid.UUID(customer_id)  # Ensure valid UUID format
            Customer.objects.get(pk=customer_id)
        except (ValueError, TypeError, Customer.DoesNotExist) as e:
            return build_response(1, "Invalid customer ID format OR Customer does not exist.", str(e), status.HTTP_404_NOT_FOUND)
        
        # Fetch Pending, Completed status IDs
        try:
            pending_status = OrderStatuses.objects.get(status_name="Pending").order_status_id
            completed_status = OrderStatuses.objects.get(status_name="Completed").order_status_id
        except ObjectDoesNotExist:
            return build_response(1, "Required order statuses 'Pending' or 'Completed' not found.", None, status.HTTP_404_NOT_FOUND)
        
        if data.get('adjustNow'):
            data_list = request.data
            
            #Making LIST Obj
            if isinstance(data_list, dict):
                data_list = [data_list]

            results = []

            try:
                with transaction.atomic():
                    for data in data_list:
                        # Validate and convert adjustNow using Decimal
                        try:
                            input_adjustNow = Decimal(data.get('adjustNow', 0)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
                            if input_adjustNow <= 0:
                                return build_response(0, "Adjust Now Amount Must Be Positive.", None, status.HTTP_406_NOT_ACCEPTABLE)
                        except (ValueError, TypeError):
                            return build_response(0, "Invalid Adjust Now Amount Provided.", None, status.HTTP_406_NOT_ACCEPTABLE)
                        
                        # Fetch sale_invoice_id using invoice_no.
                        try:
                            invoice = SaleInvoiceOrders.objects.get(invoice_no=data.get('invoice_no'))
                            total_amount = invoice.total_amount
                            bal_amt = invoice.balance_amount
                        except SaleInvoiceOrders.DoesNotExist:
                            return build_response(1, f"Sale Invoice ID with invoice no '{data.get('invoice_no')}' does not exist.", None, status.HTTP_404_NOT_FOUND)
                        
                        #checking outstanding_amount is correct or not
                        if invoice.order_status_id.status_name != "Completed":
                            # Check if the related OrderStatuses' status_name is "Completed" 
                            if Decimal(bal_amt).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)  ==  Decimal(data.get('outstanding_amount', 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):
                                #Verifying outstanding_amount
                                try:
                                    outstanding_amount = Decimal(data.get('outstanding_amount', 0))
                                except (ValueError, TypeError):
                                    return build_response(0, "Invalid Outstanding Amount Provided.", None, status.HTTP_406_NOT_ACCEPTABLE)
                                if outstanding_amount == 0:
                                    return build_response(0, "No Outstanding Amount", None, status.HTTP_400_BAD_REQUEST)
                                
                                # Calculate allocated amount, new outstanding, and remaining_payment
                                if input_adjustNow > outstanding_amount:
                                    allocated_amount = outstanding_amount
                                    new_outstanding = Decimal("0.00")
                                    remaining_payment = input_adjustNow - outstanding_amount
                                else:
                                    allocated_amount = input_adjustNow
                                    new_outstanding = outstanding_amount - input_adjustNow
                                    remaining_payment = Decimal("0.00")

                                # Create PaymentTransactions record.
                                payment_transaction = PaymentTransactions.objects.create(
                                    payment_receipt_no=data.get('payment_receipt_no'),
                                    payment_method=data.get('payment_method'),
                                    total_amount=total_amount,
                                    outstanding_amount=new_outstanding,
                                    adjusted_now=allocated_amount,
                                    payment_status=data.get('payment_status'),
                                    sale_invoice=invoice, 
                                    invoice_no=invoice.invoice_no,
                                    customer=customer_id,
                                    account_id=account_id
                                )
                                
                                # If the invoice is fully paid, update its order_status_id to "Completed".
                                if new_outstanding == Decimal('0.00'):
                                    SaleInvoiceOrders.objects.filter(sale_invoice_id=invoice.sale_invoice_id).update(order_status_id=completed_status)
                                    PaymentTransactions.objects.filter(sale_invoice_id=invoice.sale_invoice_id).update(payment_status="Completed")
                            else:
                                return build_response(0, f"Wrong outstanding_amount given your correct outstanding_amount is {bal_amt}", None, status.HTTP_400_BAD_REQUEST)
                        else:
                            return build_response(0, "Invoice Already Completed", None, status.HTTP_400_BAD_REQUEST)

                        journal_entry_line_response = JournalEntryLinesAPIView.post(self, customer_id, account_id, input_adjustNow, description, remaining_payment)
                        customer_balance_response = CustomerBalanceView.post(self, request, customer_id, remaining_payment)
                        
                        results.append({
                            "Transaction ID": str(payment_transaction.transaction_id),
                            "Total Invoice Amount": str(total_amount),
                            "Allocated Amount To Invoice": str(allocated_amount),
                            "New Outstanding": str(new_outstanding),
                            "Payment Receipt No": payment_transaction.payment_receipt_no,
                            "Remaining Payment" : str(remaining_payment),
                            "account_id" : str(account_id),
                            "journal_entry_line" : journal_entry_line_response.data.get("message"),
                            "customer_balance" : customer_balance_response.data.get("message")
                        })

                            
            except Exception as e:
                # General exception handling - the transaction will be rolled back.
                traceback.print_exc(e)        # for checking Error in Details
                return build_response(1, "An error occurred", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            return build_response(len(results), "Payment transactions processed successfully", results, status.HTTP_201_CREATED)
        else:
            # Validate and convert amount
            try:
                # Convert the incoming amount into a Decimal for accurate arithmetic & Round the amount to 4 decimal places
                input_amount = Decimal(data.get('amount', 0)).quantize(Decimal('0.0001'), rounding=ROUND_HALF_UP)
                if input_amount <= 0:
                    return build_response(1, "Amount must be positive", None, status.HTTP_406_NOT_ACCEPTABLE)
            except (ValueError, TypeError):
                return build_response(1, "Invalid amount provided.", None, status.HTTP_406_NOT_ACCEPTABLE)
            
            remaining_amount = input_amount
            payment_transactions_created = []

            # Step 1: Get all pending invoices (ordered by date)
            pending_invoices = SaleInvoiceOrders.objects.filter(
                customer_id=customer_id,
                order_status_id=pending_status
            ).order_by('invoice_date').only('sale_invoice_id', 'invoice_no', 'total_amount', 'order_status_id')

            pending_invoice_ids = pending_invoices.values_list('sale_invoice_id', flat=True)

            # Step 2: Find invoices that already have partial payments
            invoices_with_partial_payments = PaymentTransactions.objects.filter(
                sale_invoice_id__in=pending_invoice_ids,
                customer_id=customer_id).values('sale_invoice_id').annotate(total_paid=Sum('amount')).order_by('sale_invoice_id')

            # Step 3: Combine both lists (remove duplicates, sort by oldest)
            invoice_dict = {invoice.sale_invoice_id: invoice for invoice in pending_invoices}

            for invoice_data in invoices_with_partial_payments:
                sale_invoice_id = invoice_data['sale_invoice_id']
                if sale_invoice_id in invoice_dict:
                    # Update the total_paid value in the dictionary
                    invoice_dict[sale_invoice_id].total_paid = invoice_data['total_paid']
                else:
                    # If the invoice is not already in PaymentTransactions, add it manually
                    invoice_dict[sale_invoice_id] = SaleInvoiceOrders.objects.get(sale_invoice_id=sale_invoice_id)
                    invoice_dict[sale_invoice_id].total_paid = invoice_data['total_paid']

            # Convert dictionary to sorted list (oldest to newest based on created_at)
            invoices_sorted = sorted(invoice_dict.values(), key=lambda x: x.created_at)
            if invoices_sorted:
                # Process payment transactions
                with transaction.atomic():
                    # Step 4: Allocate payments to those invoices
                    for sale_invoice in invoices_sorted:
                        if remaining_amount <= 0:
                            break

                        total_paid = getattr(sale_invoice, 'total_paid', Decimal('0.0000')) or Decimal('0.0000')

                        # Check if invoice exists in PaymentTransactions and fetch outstanding_amount
                        payment_transaction = PaymentTransactions.objects.filter(sale_invoice_id=sale_invoice.sale_invoice_id).order_by('-created_at').first()
                        if payment_transaction:
                            # If invoice is in PaymentTransactions, directly use the last outstanding amount
                            current_outstanding = max(payment_transaction.outstanding_amount, Decimal('0.0000'))
                        else:
                            # If invoice is NOT in PaymentTransactions, calculate from total_amount
                            current_outstanding = max(sale_invoice.total_amount - total_paid, Decimal('0.0000'))
                        if current_outstanding <= 0:
                            continue  # Skip invoices that are fully paid

                        allocated_amount = min(remaining_amount, current_outstanding)
                        new_outstanding = current_outstanding - allocated_amount
                        remaining_amount -= allocated_amount

                        # Create payment transaction
                        payment_txn = PaymentTransactions.objects.create(
                            payment_receipt_no=data.get('payment_receipt_no'),
                            payment_method=data.get('payment_method'),
                            cheque_no=data.get('cheque_no'),
                            total_amount=sale_invoice.total_amount,
                            amount=allocated_amount,
                            outstanding_amount=new_outstanding,
                            payment_status=data.get('payment_status'),
                            customer_id=customer_id,
                            sale_invoice_id=sale_invoice.sale_invoice_id,
                            invoice_no=sale_invoice.invoice_no,
                            account_id = account_id
                        )
                        payment_transactions_created.append(payment_txn)

                        # Step 5: Update invoice status if fully paid
                        if new_outstanding == Decimal('0.00'):
                            SaleInvoiceOrders.objects.filter(sale_invoice_id=sale_invoice.sale_invoice_id).update(order_status_id=completed_status)
                            PaymentTransactions.objects.filter(sale_invoice_id=sale_invoice.sale_invoice_id).update(payment_status="Completed")
                                            
                    journal_entry_line_response = JournalEntryLinesAPIView.post(self, customer_id, account_id, input_amount, description, remaining_amount)
                    customer_balance_response = CustomerBalanceView.post(self, request, customer_id, remaining_amount)

                # Prepare response
                response_data = {
                    "payment_transactions": [
                        {
                            "Transaction ID": str(txn.transaction_id),
                            "payment Receipt No": txn.payment_receipt_no,
                            "Total Invoice Amount" : str(txn.total_amount),
                            "Amount": str(txn.amount),
                            "Outstanding Amount": str(txn.outstanding_amount),
                            "Sale Invoice Id": txn.sale_invoice_id,
                            "Invoice No": txn.invoice_no,
                            "customer_id" : str(customer_id),
                            "account_id" : str(account_id),
                            "journal_entry_line" : journal_entry_line_response.data.get("message"),
                            "customer_balance" : customer_balance_response.data.get("message")
                        }
                        for txn in payment_transactions_created
                    ],
                    "remaining_payment": str(remaining_amount)
                }
                return build_response(len(payment_transactions_created), "Payment transactions processed successfully", response_data, status.HTTP_201_CREATED)
            else:
                return build_response(0, "No Invoices", [], status.HTTP_204_NO_CONTENT)


    def get(self, request, customer_id = None):
        if customer_id:
            '''Fetch All Payment Transactions for a Customer'''
            payment_transactions = PaymentTransactions.objects.filter(customer_id=customer_id).select_related('sale_invoice').order_by('-created_at')
            
            if not payment_transactions.exists():
                return build_response(0, "No payment transactions found for this customer", None, status.HTTP_404_NOT_FOUND) 

            try:
                serializer = PaymentTransactionSerializer(payment_transactions, many=True)
                return build_response(len(serializer.data), "Payment Transactions", serializer.data, status.HTTP_200_OK)
            except Exception as e:
                return build_response(0, "An error occurred", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            transactions = PaymentTransactions.objects.all()
            serializer = PaymentTransactionSerializer(transactions, many=True)
            return build_response(len(serializer.data), "Payment Transactions", serializer.data, status.HTTP_200_OK)

class FetchSalesInvoicesForPaymentReceiptTable(APIView):
    '''This API is used to fetch all information related to sales invoices for 
        the Payment Receipt. It's related to the Payment Transaction table only.'''
    def get(self, request, customer_id):
        sale_invoice = SaleInvoiceOrders.objects.filter(customer_id=customer_id)
        
        if not sale_invoice.exists():
            return build_response(0, "No sale invoice found for this customer", None, status.HTTP_404_NOT_FOUND) 

        try:
            serializer = SaleInvoiceOrdersSerializer(sale_invoice, many=True)
            sorted_data = sorted(
                serializer.data,
                key=lambda x: x['created_at']
            )
            return build_response(len(serializer.data), "Sale Invoices", sorted_data, status.HTTP_200_OK)
        except Exception as e:
            return build_response(0, "An error occurred", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
