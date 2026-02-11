from apps.auditlogs.utils import log_user_action
from apps.masters.template.sales.sales_doc import sale_order_sales_invoice_data, sale_order_sales_invoice_doc
from apps.masters.template.table_defination import doc_heading
from apps.production.models import WorkOrder
from config.utils_methods import build_whatsapp_click_url, path_generate, resolve_phone_from_document, send_whatsapp_message_via_wati, update_multi_instances, update_product_stock, validate_input_pk, delete_multi_instance, generic_data_creation, get_object_or_none, list_all_objects, create_instance, update_instance, soft_delete, build_response, validate_multiple_data, validate_order_type, validate_payload_data, validate_put_method_data
from config.utils_filter_methods import filter_response, list_filtered_objects
from apps.inventory.models import BlockedInventory, InventoryBlockConfig
from apps.finance.models import JournalEntryLines, PaymentTransaction
from apps.customfields.serializers import CustomFieldValueSerializer
from django.db.models import F,Q, Sum, F, ExpressionWrapper,Value
from django_filters.rest_framework import DjangoFilterBackend
from apps.products.models import Products, ProductVariation
from apps.finance.views import JournalEntryLinesAPIView
from django.core.exceptions import  ObjectDoesNotExist
from apps.customfields.models import CustomFieldValue
from apps.customer.views import CustomerBalanceView
from apps.finance.models import JournalEntryLines, PaymentTransaction, ChartOfAccounts
from apps.customer.models import CustomerBalance, LedgerAccounts
from rest_framework.filters import OrderingFilter
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets, status
from apps.masters.models import OrderTypes
from decimal import Decimal, ROUND_HALF_UP
from config.utils_db_router import set_db
from rest_framework.views import APIView
from django.forms import model_to_dict
from django.db.models import Sum, Q
from apps.users.models import User
from django.utils import timezone
from django.db import transaction
from rest_framework import status
from django.http import Http404
from datetime import timedelta
from django.apps import apps
from itertools import chain
from decimal import Decimal
from .serializers import *
from .filters import *
from .models import *
import traceback
import logging
import uuid
import json
import time

workflow_progression_dict = {}
# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)


class SaleOrderView(viewsets.ModelViewSet):
    queryset = SaleOrder.objects.all().order_by('is_deleted', '-created_at')
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
        """
        Custom create for Sale Register - handles file upload and auto-populates order_type_id.
        
        Frontend can send:
        Option 1: multipart/form-data with file
            - order_id: sale_invoice_id
            - file: the actual file
            - attachment_name (optional): custom name, defaults to filename
            
        Option 2: JSON with attachment_path
            - order_id: sale_invoice_id  
            - attachment_name: name of attachment
            - attachment_path: path to already uploaded file
        """
        import os
        from uuid import uuid4
        from django.conf import settings
        
        data = request.data.copy() if hasattr(request.data, 'copy') else dict(request.data)
        
        # Handle file upload if file is present
        uploaded_file = request.FILES.get('file')
        if uploaded_file:
            # Create upload directory
            upload_dir = os.path.join(settings.MEDIA_ROOT, 'order_attachments')
            os.makedirs(upload_dir, exist_ok=True)
            
            # Generate unique filename
            file_extension = uploaded_file.name.split('.')[-1] if '.' in uploaded_file.name else ''
            unique_id = uuid4().hex[:8]
            safe_filename = f"{unique_id}_{uploaded_file.name}".replace(' ', '_')
            file_path = os.path.join(upload_dir, safe_filename)
            
            # Save file
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # Set attachment_path relative to MEDIA_ROOT
            data['attachment_path'] = f"order_attachments/{safe_filename}"
            
            # Set attachment_name if not provided
            if not data.get('attachment_name'):
                data['attachment_name'] = uploaded_file.name
        
        # Auto-populate order_type_id if not provided (for Sale Register use case)
        if not data.get('order_type_id'):
            # Get Sale Invoice order type
            order_type = get_object_or_none(OrderTypes, name='Sale Invoice')
            if order_type:
                data['order_type_id'] = str(order_type.order_type_id)
            else:
                # Fallback: try to get any order type
                order_type = OrderTypes.objects.first()
                if order_type:
                    data['order_type_id'] = str(order_type.order_type_id)
        
        # Create serializer with modified data
        serializer = self.get_serializer(data=data)
        
        if serializer.is_valid():
            instance = serializer.save()
            return build_response(1, "Attachment created successfully", serializer.data, status.HTTP_201_CREATED)
        else:
            return build_response(0, "Form validation failed", [], errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)


class QuickPacksItemsView(viewsets.ModelViewSet):
    queryset = QuickPackItems.objects.all()
    serializer_class = QuickPackItemSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
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
from django.conf import settings

def try_send_sale_order_whatsapp(request, sale_order_id):
    """
    Best-effort WhatsApp sender
    Silent, non-blocking
    Local = skip but prove working
    """
    try:
        from django.conf import settings

        # ------------------ PHONE RESOLUTION ------------------ #
        city_id = request.GET.get('city')

        phone = resolve_phone_from_document(
            document_type="sale_order",
            pk=sale_order_id,
            city_id=city_id
        )

        if not phone:
            return {
                "whatsapp_sent": False,
                "mode": "none",
                "reason": "PHONE_NOT_FOUND"
            }

        # ------------------ FETCH SALE ORDER ------------------ #
        sale_order = SaleOrder.objects.filter(sale_order_id=sale_order_id).first()
        customer_name = (
            sale_order.customer.name
            if sale_order and sale_order.customer
            else "Customer"
        )

        # ------------------ MESSAGE CONTENT ------------------ #
        message_text = (
            f"Hey {customer_name}, your order has been placed successfully. "
            f"If you need order details, please contact us."
        )

        # ------------------ LOCAL / WATI DISABLED ------------------ #
        if not getattr(settings, 'ENABLE_WATI', False):
            logger.info("WhatsApp skipped (local / click-to-chat)")
            logger.info(f"Phone : {phone}")
            logger.info(f"Message : {message_text}")

            return {
                "whatsapp_sent": False,
                "mode": "click_to_chat",
                "reason": "WATI_DISABLED",
                "phone": phone,
                "message": message_text
            }

        # ------------------ PRODUCTION (WATI) ------------------ #
        send_whatsapp_message_via_wati(
            to_number=phone,
            message_text=message_text
        )

        return {
            "whatsapp_sent": True,
            "mode": "wati",
            "phone": phone
        }

    except Exception as e:
        logger.warning(f"WhatsApp failed for SaleOrder {sale_order_id}: {e}")
        return {
            "whatsapp_sent": False,
            "mode": "error",
            "reason": "WHATSAPP_ERROR"
        }



class SaleOrderViewSet(APIView):
    """API ViewSet for handling sale order creation and related data."""
    def get_object(self, pk):
        try:
            return SaleOrder.objects.get(pk=pk)
        except SaleOrder.DoesNotExist:
            logger.warning(f"SaleOrder with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

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
            
            if request.query_params.get("records_mstcnl", "false").lower() == "true" :
                return self.get_summary_data(request)
            
            if request.query_params.get("sales_order_report", "false").lower() == "true" :
                return self.get_sales_order_report(request)
            
            # if request.query_params.get("sales_invoice_report", "false").lower() == "true" :
            #     return self.get_sales_invoice_report(request)
            
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
        
        queryset = SaleOrder.objects.all().order_by('is_deleted', '-created_at')

        if request.query_params:
            filterset = SaleOrderFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = SaleOrder.objects.count()
        serializer = SaleOrderSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    # def get_summary_data(self, request):
    #     """Fetches sale order summary data from both databases."""
    #     logger.info("Retrieving Sale order summary")
        
    #     # Get pagination parameters with defaults
    #     page = int(request.query_params.get("page", 1))
    #     limit = int(request.query_params.get("limit", 0))  # 0 means no limit
    #     records_all = request.query_params.get("records_all", "false").lower() == "true"
    #     records_mstcnl = request.query_params.get("records_mstcnl", "false").lower() == "true"

    #     # Extract sort parameter from request
    #     sort_param = request.GET.get('sort[0]', '-created_at')
    #     if sort_param:
    #         if ',' in sort_param:
    #             field, direction = sort_param.split(',')
    #             sort_field = f'-{field}' if direction.upper() == 'DESC' else field
    #         else:
    #             sort_field = sort_param
    #     else:
    #         sort_field = '-created_at'

    #     if records_all:
    #         logger.info("Fetching sale order summary from both mstcnl and default databases")

    #         # Apply base ordering to both databases
    #         base_queryset_mstcnl = MstcnlSaleOrder.objects.using('mstcnl').all().order_by(sort_field)
    #         base_queryset_devcnl = SaleOrder.objects.using('default').all().order_by(sort_field)

    #         # Create copies of GET params without sort for filtering
    #         filter_params = request.GET.copy()
    #         if 'sort[0]' in filter_params:
    #             del filter_params['sort[0]']
    #         if 'sort' in filter_params:
    #             del filter_params['sort']

    #         # Apply filters
    #         filterset_mstcnl = MstcnlSaleOrderFilter(filter_params, queryset=base_queryset_mstcnl)
    #         saleorders_mstcnl = filterset_mstcnl.qs if filterset_mstcnl.is_valid() else base_queryset_mstcnl
            
    #         filterset_devcnl = SaleOrderFilter(filter_params, queryset=base_queryset_devcnl)
    #         saleorders_devcnl = filterset_devcnl.qs if filterset_devcnl.is_valid() else base_queryset_devcnl

    #         # Get TOTAL counts (this should be 21 in your case)
    #         count_mstcnl = saleorders_mstcnl.count()
    #         count_devcnl = saleorders_devcnl.count()
    #         total_count = count_mstcnl + count_devcnl  # This should be 21

    #         # Check if pagination is requested (limit > 0)
    #         if limit > 0:
    #             # Calculate pagination ranges
    #             items_per_page = limit
    #             current_page = page
    #             start_index = (current_page - 1) * items_per_page
    #             end_index = start_index + items_per_page

    #             # Determine how many items to take from each database
    #             if start_index < count_mstcnl:
    #                 mstcnl_end = min(end_index, count_mstcnl)
    #                 mstcnl_count = mstcnl_end - start_index
    #                 devcnl_count = max(0, end_index - count_mstcnl)
    #             else:
    #                 mstcnl_count = 0
    #                 devcnl_count = items_per_page

    #             # Fetch paginated data
    #             paginated_mstcnl = []
    #             if mstcnl_count > 0:
    #                 paginated_mstcnl = saleorders_mstcnl[start_index:start_index + mstcnl_count]
                
    #             paginated_devcnl = []
    #             if devcnl_count > 0:
    #                 devcnl_start = max(0, start_index - count_mstcnl)
    #                 paginated_devcnl = saleorders_devcnl[devcnl_start:devcnl_start + devcnl_count]
    #         else:
    #             # No pagination - get all records
    #             paginated_mstcnl = saleorders_mstcnl
    #             paginated_devcnl = saleorders_devcnl

    #         # Serialize the results
    #         serializer_mstcnl = MstcnlSaleOrderSerializer(paginated_mstcnl, many=True)
    #         serializer_devcnl = SaleOrderSerializer(paginated_devcnl, many=True)

    #         # Combine results
    #         final_results = serializer_mstcnl.data + serializer_devcnl.data

    #         # If no limit specified, return all records without pagination metadata
    #         if limit <= 0:
    #             return Response({
    #                 "count": len(final_results),  # This will be 21
    #                 "message": "Success",
    #                 "data": final_results,
    #                 "totalCount": total_count  # This will also be 21
    #             }, status=status.HTTP_200_OK)
    #         else:
    #             # For paginated response, use total_count (21) instead of len(final_results) (10)
    #             return filter_response(
    #                 len(final_results),  # Current page count (10)
    #                 "Success",
    #                 final_results,
    #                 page,
    #                 limit,
    #                 total_count,  # Total across all databases (21)
    #                 status.HTTP_200_OK
    #             )
    #     elif records_mstcnl:        
    #         logger.info("Fetching sale orders only from mstcnl database")

    #         base_queryset_mstcnl = MstcnlSaleOrder.objects.using('mstcnl').all().order_by('-created_at')

    #         filterset_mstcnl = MstcnlSaleOrderFilter(request.GET, queryset=base_queryset_mstcnl)
    #         if filterset_mstcnl.is_valid():
    #             saleorders_mstcnl = filterset_mstcnl.qs
    #         else:
    #             saleorders_mstcnl = base_queryset_mstcnl

    #         total_count = saleorders_mstcnl.count()
    #         start_index = (page - 1) * limit
    #         end_index = start_index + limit
    #         paginated_results = saleorders_mstcnl[start_index:end_index]

    #         serializer_mstcnl = MstcnlSaleOrderSerializer(paginated_results, many=True)

    #         return filter_response(
    #             total_count,
    #             "Success",
    #             serializer_mstcnl.data,
    #             page,
    #             limit,
    #             total_count,
    #             status.HTTP_200_OK
    #         )

    #     else:
    #         logger.info("Fetching sale order summary only from default database")
    #         queryset = SaleOrder.objects.all().order_by('is_deleted', '-created_at')

    #         # Dynamically fetch the IDs
    #         other_sale_type_id = SaleTypes.objects.filter(name="Other").values_list("sale_type_id", flat=True).first()
    #         completed_flow_status_id = FlowStatus.objects.filter(flow_status_name="Completed").values_list("flow_status_id", flat=True).first()


    #         # ✅ Exclude if both IDs are present
    #         if other_sale_type_id and completed_flow_status_id:
    #             queryset = queryset.exclude(
    #                 sale_type_id=other_sale_type_id,
    #                 flow_status_id=completed_flow_status_id
    #             )
            
    #         if request.query_params:
    #             filterset = SaleOrderFilter(request.GET, queryset=queryset)
    #             if filterset.is_valid():
    #                 queryset = filterset.qs
                    
    #         page = int(request.query_params.get('page', 1))
    #         limit = int(request.query_params.get('limit', 10))
    #         total_count = queryset.count()
    #         # ✅ Apply pagination
    #         start_index = (page - 1) * limit
    #         end_index = start_index + limit
    #         # paginated_results = queryset[start_index:end_index]
    #         paginated_results = queryset[(page - 1) * limit: page * limit]
    #         # paginated_results = queryset[(page - 1) * limit: page * limit]

    #         serializer = SaleOrderOptionsSerializer(paginated_results, many=True)
    #         return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)


    def get_summary_data(self, request):
        """Fetches sale order summary data from both databases."""
        logger.info("Retrieving Sale order summary")
        
        # Get pagination parameters with defaults
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        records_all = request.query_params.get("records_all", "false").lower() == "true"
        records_mstcnl = request.query_params.get("records_mstcnl", "false").lower() == "true"

        # Extract sort parameter from request
        sort_param = request.GET.get('sort[0]', '-created_at')
        if sort_param:
            if ',' in sort_param:
                field, direction = sort_param.split(',')
                sort_field = f'-{field}' if direction.upper() == 'DESC' else field
            else:
                sort_field = sort_param
        else:
            sort_field = '-created_at'

        if records_all:
            logger.info("Fetching ALL sale order summary from both mstcnl and default databases (no pagination)")

            # Apply base ordering to both databases
            base_queryset_mstcnl = MstcnlSaleOrder.objects.using('mstcnl').all().order_by(sort_field)
            base_queryset_devcnl = SaleOrder.objects.using('default').all().order_by(sort_field)

            # Create copies of GET params without sort for filtering
            filter_params = request.GET.copy()
            if 'sort[0]' in filter_params:
                del filter_params['sort[0]']
            if 'sort' in filter_params:
                del filter_params['sort']
            # Also remove pagination parameters for filtering
            if 'page' in filter_params:
                del filter_params['page']
            if 'limit' in filter_params:
                del filter_params['limit']

            # Apply filters
            filterset_mstcnl = MstcnlSaleOrderFilter(filter_params, queryset=base_queryset_mstcnl)
            saleorders_mstcnl = filterset_mstcnl.qs if filterset_mstcnl.is_valid() else base_queryset_mstcnl
            
            filterset_devcnl = SaleOrderFilter(filter_params, queryset=base_queryset_devcnl)
            saleorders_devcnl = filterset_devcnl.qs if filterset_devcnl.is_valid() else base_queryset_devcnl

            # Get all records (no pagination)
            all_mstcnl_records = saleorders_mstcnl
            all_devcnl_records = saleorders_devcnl

            # Serialize the results
            serializer_mstcnl = MstcnlSaleOrderSerializer(all_mstcnl_records, many=True)
            serializer_devcnl = SaleOrderSerializer(all_devcnl_records, many=True)

            # Combine results
            final_results = serializer_mstcnl.data + serializer_devcnl.data
            total_count = len(final_results)

            # Return ALL records without pagination metadata
            return Response({
                "count": total_count,
                "message": "Success",
                "data": final_results,
                "totalCount": total_count
            }, status=status.HTTP_200_OK)
        
        elif records_mstcnl:        
            logger.info("Fetching sale orders only from mstcnl database")

            base_queryset_mstcnl = MstcnlSaleOrder.objects.using('mstcnl').all().order_by('-created_at')

            filterset_mstcnl = MstcnlSaleOrderFilter(request.GET, queryset=base_queryset_mstcnl)
            if filterset_mstcnl.is_valid():
                saleorders_mstcnl = filterset_mstcnl.qs
            else:
                saleorders_mstcnl = base_queryset_mstcnl

            total_count = saleorders_mstcnl.count()
            start_index = (page - 1) * limit
            end_index = start_index + limit
            paginated_results = saleorders_mstcnl[start_index:end_index]
            
            current_page_count = len(paginated_results)  # Count of items on current page

            serializer_mstcnl = MstcnlSaleOrderSerializer(paginated_results, many=True)

            return filter_response(
                current_page_count,  # Items on current page
                "Success",
                serializer_mstcnl.data,
                page,
                limit,
                total_count,  # Total items
                status.HTTP_200_OK
            )
            
        else:
            logger.info("Fetching sale order summary only from default database")
            
            # Start with all records
            queryset = SaleOrder.objects.all().order_by('is_deleted', '-created_at')

            # Apply filters from request FIRST (before any slicing)
            if request.query_params:
                # Create a copy of GET params to avoid modifying the original request
                filter_params = request.GET.copy()
                
                # Remove pagination parameters to avoid conflicts with filtering
                if 'page' in filter_params:
                    del filter_params['page']
                if 'limit' in filter_params:
                    del filter_params['limit']
                    
                filterset = SaleOrderFilter(filter_params, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs

            # Now apply the exclusion for "Other" and "Completed"
            other_sale_type_id = SaleTypes.objects.filter(name="Other").values_list("sale_type_id", flat=True).first()
            completed_flow_status_id = FlowStatus.objects.filter(flow_status_name="Completed").values_list("flow_status_id", flat=True).first()

            if other_sale_type_id and completed_flow_status_id:
                queryset = queryset.exclude(
                    sale_type_id=other_sale_type_id,
                    flow_status_id=completed_flow_status_id
                )

            # Get total count AFTER all filtering and exclusions
            total_count = queryset.count()
            
            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))

            # Apply pagination LAST (after all filtering)
            paginated_results = queryset[(page - 1) * limit: page * limit]
            
            # Use your existing serializer
            serializer = SaleOrderOptionsSerializer(paginated_results, many=True)

            return filter_response(
                total_count,        # Total count of all matching records
                "Success", 
                serializer.data, 
                page, 
                limit, 
                total_count,        # Same total count
                status.HTTP_200_OK
            )

        # else:
        #     logger.info("Fetching sale order summary only from default database")
        #     queryset = SaleOrder.objects.all().order_by('is_deleted', '-created_at')

        #     # Dynamically fetch the IDs
        #     other_sale_type_id = SaleTypes.objects.filter(name="Other").values_list("sale_type_id", flat=True).first()
        #     completed_flow_status_id = FlowStatus.objects.filter(flow_status_name="Completed").values_list("flow_status_id", flat=True).first()

        #     # ✅ Exclude if both IDs are present
        #     if other_sale_type_id and completed_flow_status_id:
        #         queryset = queryset.exclude(
        #             sale_type_id=other_sale_type_id,
        #             flow_status_id=completed_flow_status_id
        #         )
            
        #     if request.query_params:
        #         filterset = SaleOrderFilter(request.GET, queryset=queryset)
        #         if filterset.is_valid():
        #             queryset = filterset.qs
                    
        #     page = int(request.query_params.get('page', 1))
        #     limit = int(request.query_params.get('limit', 10))
        #     total_count = queryset.count()
            
        #     # ✅ Apply pagination
        #     paginated_results = queryset[(page - 1) * limit: page * limit]
        #     current_page_count = len(paginated_results)  # Count of items on current page

        #     serializer = SaleOrderOptionsSerializer(paginated_results, many=True)
        #     return filter_response(
        #         current_page_count,  # Items on current page
        #         "Success", 
        #         serializer.data, 
        #         page, 
        #         limit, 
        #         total_count,  # Total items
        #         status.HTTP_200_OK
        #     )

    # def get_sales_order_report(self, request):
    #     """Fetches sales order details with required fields."""
    #     logger.info("Retrieving sales order report data")
    #     page, limit = self.get_pagination_params(request)

    #     # Group the necessary fields from SaleOrder model.
    #     queryset = SaleOrder.objects.all().order_by('is_deleted', '-created_at')

    #     if request.query_params:
    #         filterset = SalesOrderReportFilter(request.GET, queryset=queryset)
    #         if filterset.is_valid():
    #             queryset = filterset.qs
                
    #     total_count = SaleOrder.objects.count()
    #     serializer = SalesOrderReportSerializer(queryset, many=True)
    #     return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
    
    # def get_sales_order_report(self, request):
    #     """Fetches sales order details with required fields."""
    #     logger.info("Retrieving sales order report data")
    #     page, limit = self.get_pagination_params(request)
    #     report_type = request.query_params.get("report_type", "regular").lower()

    #     if report_type == "all":
    #         logger.info("Fetching sales order report from both mstcnl and default databases")

    #         queryset_default = SaleOrder.objects.using('default').all().order_by('is_deleted', '-created_at')
    #         queryset_mstcnl = SaleOrder.objects.using('mstcnl').all().order_by('is_deleted', '-created_at')
    #         combined_queryset = list(chain(queryset_default, queryset_mstcnl))

    #         total_count = len(combined_queryset)
    #         start_index = (page - 1) * limit
    #         end_index = start_index + limit
    #         paginated_results = combined_queryset[start_index:end_index]

    #         serializer = SalesOrderReportSerializer(paginated_results, many=True)
    #         return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

    #     elif report_type == "other":
    #         logger.info("Fetching sales order report from mstcnl database")
    #         queryset = SaleOrder.objects.using('mstcnl').all().order_by('is_deleted', '-created_at')

    #     else:  # default to 'regular'
    #         logger.info("Fetching sales order report from default database")
    #         queryset = SaleOrder.objects.using('default').all().order_by('is_deleted', '-created_at')

    #     if request.query_params:
    #         filterset = SalesOrderReportFilter(request.GET, queryset=queryset)
    #         if filterset.is_valid():
    #             queryset = filterset.qs

    #     total_count = queryset.count()
    #     paginated_results = queryset[(page - 1) * limit: page * limit]
    #     serializer = SalesOrderReportSerializer(paginated_results, many=True)
    #     return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)
    
    def get_sales_order_report(self, request):
        """Fetches sales order details with required fields."""
        logger.info("Retrieving sales order report data")
        page, limit = self.get_pagination_params(request)
        report_type = request.query_params.get("report_type", "regular").lower()

        if report_type == "all":
            logger.info("Fetching sales order report from both mstcnl and default databases")

            queryset_default = SaleOrder.objects.using('default').all().order_by('is_deleted', '-created_at')
            queryset_mstcnl = MstcnlSaleOrder.objects.using('mstcnl').all().order_by('is_deleted', '-created_at')

            combined_queryset = list(chain(queryset_default, queryset_mstcnl))
            total_count = len(combined_queryset)

            start_index = (page - 1) * limit
            end_index = start_index + limit
            paginated_results = combined_queryset[start_index:end_index]

            # Separate for correct serializer if needed
            paginated_mstcnl = [obj for obj in paginated_results if isinstance(obj, MstcnlSaleOrder)]
            paginated_devcnl = [obj for obj in paginated_results if isinstance(obj, SaleOrder)]

            serializer_mstcnl = MstcnlSaleOrderSerializer(paginated_mstcnl, many=True)
            serializer_devcnl = SalesOrderReportSerializer(paginated_devcnl, many=True)

            final_results = serializer_mstcnl.data + serializer_devcnl.data

            return filter_response(total_count, "Success", final_results, page, limit, total_count, status.HTTP_200_OK)

        elif report_type == "Other":
            logger.info("Fetching sales order report from mstcnl database")
            queryset = MstcnlSaleOrder.objects.using('mstcnl').all().order_by('is_deleted', '-created_at')

        else:  # default to 'regular'
            logger.info("Fetching sales order report from default database")
            queryset = SaleOrder.objects.using('default').all().order_by('is_deleted', '-created_at')

        if request.query_params:
            filterset = SalesOrderReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = queryset.count()
        paginated_results = queryset[(page - 1) * limit: page * limit]

        # Use correct serializer for single DB
        if report_type == "Other":
            serializer = MstcnlSaleOrderSerializer(paginated_results, many=True)
        else:
            serializer = SalesOrderReportSerializer(paginated_results, many=True)

        return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)


    # def get_sales_invoice_report(self, request):
    #     """Fetches detailed sales invoice report data."""
    #     logger.info("Retrieving detailed sales invoice report data")
    #     page, limit = self.get_pagination_params(request)

    #     # NEW: Get invoice_type from query params (default is 'Regular')
    #     invoice_type = request.query_params.get('invoice_type', 'Regular')
    #     bill_type = request.query_params.get('bill_type', 'Regular')

    #     # NEW: Determine database and fetch queryset accordingly
    #     if bill_type == 'Others':
    #         queryset = MstcnlSaleInvoiceOrder.objects.using('mstcnl').all().order_by('-invoice_date')
    #         # total_count = MstcnlSaleInvoiceOrder.objects.using('mstcnl').count()
    #     elif invoice_type == 'all':
    #         logger.info("Fetching sale order summary from both mstcnl and default databases")

    #         base_queryset_mstcnl = MstcnlSaleInvoiceOrder.objects.using('mstcnl').all().order_by('is_deleted', '-created_at')
    #         filterset_mstcnl = MstcnlSaleInvoiceFilter(request.GET, queryset=base_queryset_mstcnl)
    #         saleorders_mstcnl = filterset_mstcnl.qs if filterset_mstcnl.is_valid() else base_queryset_mstcnl

    #         base_queryset_devcnl = SaleInvoiceOrders.objects.using('default').all().order_by('is_deleted', '-created_at')
    #         filterset_devcnl = SaleInvoiceOrdersFilter(request.GET, queryset=base_queryset_devcnl)
    #         saleorders_devcnl = filterset_devcnl.qs if filterset_devcnl.is_valid() else base_queryset_devcnl

    #         combined_queryset = list(chain(saleorders_mstcnl, saleorders_devcnl))
    #         total_count = len(combined_queryset)

    #         start_index = (page - 1) * limit
    #         end_index = start_index + limit
    #         paginated_results = combined_queryset[start_index:end_index]

    #         paginated_mstcnl = [obj for obj in paginated_results if isinstance(obj, MstcnlSaleOrder)]
    #         paginated_devcnl = [obj for obj in paginated_results if isinstance(obj, SaleOrder)]

    #         serializer_mstcnl = MstcnlSaleInvoiceSerializer(paginated_mstcnl, many=True)
    #         serializer_devcnl = SaleInvoiceOrdersSerializer(paginated_devcnl, many=True)

    #         final_results = serializer_mstcnl.data + serializer_devcnl.data

    #         return filter_response(
    #             total_count,
    #             "Success",
    #             final_results,
    #             page,
    #             limit,
    #             total_count,
    #             status.HTTP_200_OK
    #         )

    #     else:  # Default to Regular
    #         queryset = SaleInvoiceOrders.objects.all().order_by('-invoice_date')
    #         total_count = SaleInvoiceOrders.objects.count()

    #     # Existing filtering logic
    #     if request.query_params:
    #         filterset = SalesInvoiceReportFilter(request.GET, queryset=queryset)
    #         if filterset.is_valid():
    #             queryset = filterset.qs

    #     serializer = SalesInvoiceReportSerializer(queryset, many=True)
    #     return filter_response(
    #         queryset.count() if hasattr(queryset, 'count') else len(queryset),
    #         "Success",
    #         serializer.data,
    #         page,
    #         limit,
    #         total_count,
    #         status.HTTP_200_OK
    #     )



    def get_sales_by_product(self, request):
        """Fetches total sales amount grouped by product."""
        logger.info("Retrieving sales by product data")
        page, limit = self.get_pagination_params(request)
        
        queryset = SaleOrderItems.objects.values( "product_id__name").annotate(
                total_quantity_sold=Sum("quantity"),
                total_sales=Sum("amount"),
            ).order_by('-total_sales')

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
                sale_order = MstcnlSaleOrder.objects.using('mstcnl').get(pk=pk)
                using_db = 'mstcnl'
                logger.info(f"Sale order found in 'mstcnl' database with pk: {pk}")
            except MstcnlSaleOrder.DoesNotExist:
                # Step 2: If not found in mstcnl, try devcnl (default)
                try:
                    sale_order = SaleOrder.objects.using('default').get(pk=pk)
                    using_db = 'default'
                    logger.info(f"Sale order found in 'default' database with pk: {pk}")

                    #  Use Mstcnl serializer for mstcnl
                    sale_order_serializer = MstcnlSaleOrderSerializer(sale_order)
                except SaleOrder.DoesNotExist:
                    # Step 3: Not found anywhere
                    logger.error(f"Sale order with pk {pk} does not exist in any database.")
                    return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

            # Step 4: Serialize the sale order
            # sale_order_serializer = SaleOrderSerializer(sale_order)
            
            # Step 3: Serialize the sale order
            if using_db == 'mstcnl':
                sale_order_serializer = MstcnlSaleOrderSerializer(sale_order)
            else:
                sale_order_serializer = SaleOrderSerializer(sale_order)

            # Step 4: Fetch related data using correct database
            # Step 5: Fetch related data using correct database
            if using_db == 'mstcnl':
                items_data = self.get_related_data(
                    MstcnlSaleOrderItem, MstcnlSaleOrderItemsSerializer,
                    'sale_order_id', pk, using_db
                )
                attachments_data = self.get_related_data(
                    MstcnlOrderAttachment, MstcnlOrderAttachmentsSerializer,
                    'order_id', pk, using_db
                )
                shipments_data = self.get_related_data(
                    MstcnlOrderShipment, MstcnlOrderShipmentsSerializer,
                    'order_id', pk, using_db
                )
                # custom_field_values_data = []
                custom_field_values_data = self.get_related_data(
                    MstcnlCustomFieldValue, MstcnlCustomFieldValueSerializer,
                    'custom_id', pk, using_db
                )
            else:
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

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale order and its related data.
        Before deleting, checks if the sale order is linked to any transactional data
        such as sale invoices or sale returns.
        """
        db_to_use = None
        try:
            # Get the SaleOrder instance
            instance = SaleOrder.objects.using(db_to_use).get(pk=pk)

            # --------------------------------------------
            # 1️⃣  Check for linked transactional data
            # --------------------------------------------
            linked_invoice_exists = SaleInvoiceOrders.objects.filter(sale_order_id=pk, is_deleted=False).exists()
            # linked_return_exists = SaleReturnOrders.objects.filter(sale_order_id=pk, is_deleted=False).exists()

            if linked_invoice_exists:
                # If the sale order is linked to invoices or returns, do not delete
                logger.warning(f"SaleOrder with ID {pk} cannot be deleted as it has transactional data.")
                return build_response(
                    0,
                    "Sale order cannot be deleted as it has transactional data",
                    [],
                    status.HTTP_400_BAD_REQUEST
                )
                
            # --------------------------------------------
            # 2. Permanent delete if no linked invoice exists
            # --------------------------------------------
            else:
                record_id = instance.pk
                # Delete related child data first
                SaleOrderItems.objects.using(db_to_use).filter(sale_order_id=pk).delete()
                BlockedInventory.objects.using(db_to_use).filter(sale_order_id=pk).delete()
                WorkOrder.objects.using(db_to_use).filter(sale_order_id=pk).delete()
                
                # No linked sale invoice → delete permanently
                instance.delete(using=db_to_use)

                # Log the permanent deletion
                log_user_action(
                    db_to_use,
                    request.user,
                    "DELETE",
                    "Sale Order",
                    pk,
                    f"Sale Order {instance.order_no} permanently deleted by {request.user.username}"
                )

                logger.info(f"SaleOrder {record_id} permanently deleted from database.")
                return build_response(1, "Sale order permanently deleted successfully.", [], status.HTTP_204_NO_CONTENT)
            
            # # --------------------------------------------
            # # 2️ Permanent Deletion for 'Other' & 'Completed'
            # # --------------------------------------------
            # try:
            #     # Fetch the correct SaleType and OrderStatus objects dynamically
            #     other_sale_type = SaleTypes.objects.using(db_to_use).get(name="Other")
            #     completed_status = OrderStatuses.objects.using(db_to_use).get(status_name="Completed")

            #     if (
            #         instance.sale_type_id == other_sale_type.sale_type_id
            #         and instance.order_status_id == completed_status.order_status_id
            #     ):
            #         logger.info(f"SaleOrder {pk} (Other & Completed) is already replicated to mstcnl, skipping delete.")
            #         return build_response(
            #             0,
            #             "Sale order already replicated to mstcnl; deletion skipped.",
            #             [],
            #             status.HTTP_400_BAD_REQUEST
            #         )

            # except (SaleTypes.DoesNotExist, OrderStatuses.DoesNotExist) as e:
            #     logger.error(f"Required SaleType or OrderStatus not found: {str(e)}")
            #     return build_response(
            #         0,
            #         "Required SaleType ('Other') or OrderStatus ('Completed') not found.",
            #         [],
            #         status.HTTP_400_BAD_REQUEST
            #     )


            # # --------------------------------------------
            # # 3 Delete related child data
            # # --------------------------------------------
            # if not delete_multi_instance(pk, SaleOrder, OrderAttachments, main_model_field_name='order_id', using_db=db_to_use):
            #     return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # if not delete_multi_instance(pk, SaleOrder, OrderShipments, main_model_field_name='order_id', using_db=db_to_use):
            #     return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # if not delete_multi_instance(pk, SaleOrder, CustomFieldValue, main_model_field_name='custom_id', using_db=db_to_use):
            #     return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # # --------------------------------------------
            # # 3️ Mark main SaleOrder as deleted
            # # --------------------------------------------
            # instance.is_deleted = True
            # instance.save(using=db_to_use)

            # logger.info(f"SaleOrder with ID {pk} deleted successfully.")
            # return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)

        except SaleOrder.DoesNotExist:
            logger.warning(f"SaleOrder with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error deleting SaleOrder with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    # @transaction.atomic
    # def delete(self, request, pk, *args, **kwargs):
    #     """
    #     Handles the deletion of a sale order and its related attachments and shipments.
    #     Based on the sale_order_id, it checks the appropriate database and deletes the records.
    #     """
    #     db_to_use = None
    #     try:
    #         # Get the SaleOrder instance from the appropriate database
    #         instance = SaleOrder.objects.using(db_to_use).get(pk=pk)

    #         # Delete related OrderAttachments, OrderShipments, and CustomFieldValues from the correct database
    #         if not delete_multi_instance(pk, SaleOrder, OrderAttachments, main_model_field_name='order_id', using_db=db_to_use):
    #             return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    #         if not delete_multi_instance(pk, SaleOrder, OrderShipments, main_model_field_name='order_id', using_db=db_to_use):
    #             return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    #         if not delete_multi_instance(pk, SaleOrder, CustomFieldValue, main_model_field_name='custom_id', using_db=db_to_use):
    #             return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    #         # Delete the main SaleOrder instance from the correct database
    #         # instance.delete(using=db_to_use)
    #         # Delete the main CustomField instance
    #         instance.is_deleted = True
    #         instance.save(using=db_to_use)

    #         logger.info(f"SaleOrder with ID {pk} deleted successfully.")
    #         return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)

    #     except SaleOrder.DoesNotExist:
    #         logger.warning(f"SaleOrder with ID {pk} does not exist.")
    #         return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         logger.error(f"Error deleting SaleOrder with ID {pk}: {str(e)}")
    #         return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
#---------------------------------------------------------

    # @transaction.atomic
    # def create(self, request, *args, **kwargs):
    #     given_data = request.data
    #     #print("-" * 30)
    #     #print("Given data:", given_data)
    #     #print("-" * 30)

    #     # Extract payload after DB is known
    #     sale_order_data = given_data.pop('sale_order', None)
    #     sale_order_items_data = given_data.pop('sale_order_items', None)
    #     order_attachments_data = given_data.pop('order_attachments', None)
    #     order_shipments_data = given_data.pop('order_shipments', None)
    #     custom_fields_data = given_data.pop('custom_field_values', None)
        
    #     # ---------------- CLEAN EMPTY SALE ORDER ITEMS ---------------- #
    #     # Remove blank/empty payloads created by frontend (5 default rows)
    #     # 👉 ADD THIS BELOW
    #     sale_order_items_data = [
    #         item for item in sale_order_items_data
    #         if item.get("product_id") and item.get("quantity")
    #     ]
    #     #----------------------------------------------------------

    #     sale_type_name = sale_order_data.get("sale_type", {}).get("name")
    #     flow_status_name = sale_order_data.get("flow_status", {}).get("flow_status_name")
    #     is_mstcnl = sale_type_name == "Other" and flow_status_name == "Completed"

    #     if is_mstcnl:
    #         try:
    #             # Flatten FKs
    #             sale_order_id = sale_order_data.get("sale_order_id")
    #             order_no = sale_order_data.get("order_no")
    #             ref_no = sale_order_data.get("ref_no")
    #             ref_date = sale_order_data.get("ref_date")
    #             order_date = sale_order_data.get("order_date")
    #             delivery_date = sale_order_data.get("delivery_date")
    #             customer_name = sale_order_data.get("customer", {}).get("name")
    #             sale_type = sale_order_data.get("sale_type", {}).get("name")
    #             flow_status = sale_order_data.get("flow_status", {}).get("flow_status_name")
    #             order_status = sale_order_data.get("order_status", {}).get("status_name")

    #             # Optional fields
    #             remarks = sale_order_data.get("remarks")
    #             email = sale_order_data.get("email")
    #             total_amount = sale_order_data.get("total_amount")
    #             item_value = sale_order_data.get("item_value")
    #             tax_amount = sale_order_data.get("tax_amount")
    #             discount = sale_order_data.get("discount")
    #             tax = sale_order_data.get("tax")
    #             sale_estimate = sale_order_data.get("sale_estimate")
    #             use_workflow = sale_order_data.get("use_workflow")
    #             shipping_address = sale_order_data.get("shipping_address")
    #             billing_address = sale_order_data.get("billing_address")

    #             # Create the record in mstcnl DB
    #             MstcnlSaleOrder.objects.using('mstcnl').create(
    #                 sale_order_id=sale_order_id,
    #                 order_no=order_no,
    #                 ref_no=ref_no,
    #                 ref_date=ref_date,
    #                 order_date=order_date,
    #                 delivery_date=delivery_date,
    #                 customer_id=customer_name,
    #                 sale_type_id=sale_type,
    #                 flow_status_id=flow_status,
    #                 order_status_id=order_status,
    #                 remarks=remarks,
    #                 email=email,
    #                 total_amount=total_amount,
    #                 item_value=item_value,
    #                 tax_amount=tax_amount,
    #                 discount=discount,
    #                 tax=tax,
    #                 sale_estimate=sale_estimate,
    #                 use_workflow=use_workflow,
    #                 shipping_address=shipping_address,
    #                 billing_address=billing_address,
    #                 created_at=timezone.now(),
    #                 updated_at=timezone.now(),
    #                 # order_type='sale_order'
    #             )

    #             logger.info(" SaleOrder created in mstcnl DB")
    #             # return build_response(1, "Sale Order replicated to mstcnl DB", {"sale_order_id": sale_order_id}, status.HTTP_201_CREATED)
        
    #             # STEP 2: Create sale_order_items in mstcnl DB
    #             for item in sale_order_items_data:
    #                 try:
    #                     MstcnlSaleOrderItem.objects.using('mstcnl').create(
    #                         sale_order_item_id=item.get("sale_order_item_id"),
    #                         sale_order_id=sale_order_id,
    #                         product_id=item.get("product", {}).get("name"),
    #                         # code=item.get("product", {}).get("code"),
    #                         # print_name=item.get("print_name"),
    #                         unit_options_id=item.get("unit_options", {}).get("unit_name"),
    #                         size_id=item.get("size", {}).get("size_name"),
    #                         color_id=item.get("color", {}).get("color_name"),
    #                         quantity=item.get("quantity"),
    #                         rate=item.get("rate"),
    #                         amount=item.get("amount"),
    #                         discount=item.get("discount"),
    #                         tax=item.get("tax"),
    #                         cgst=item.get("cgst"),
    #                         sgst=item.get("sgst"),
    #                         igst=item.get("igst"),
    #                         invoiced=item.get("invoiced"),
    #                         work_order_created=item.get("work_order_created"),
    #                         remarks=item.get("remarks"),
    #                         created_at=timezone.now(),
    #                         updated_at=timezone.now(),
                            
    #                     )
    #                     logger.info(" SaleOrder items created in mstcnl DB")
    #                     # return build_response(1, "Sale Order items replicated to mstcnl DB", {"sale_order_item_id": item.get('sale_order_item_id')}, status.HTTP_201_CREATED)
    #                 except Exception as e:
    #                     logger.warning(f"❌ Failed to replicate SaleOrderItem {item.get('sale_order_item_id')} to mstcnl DB: {e}")

    #             #  Attachments: only if present and list
    #             if order_attachments_data and isinstance(order_attachments_data, list):
    #                 for attachment in order_attachments_data:
    #                     try:
    #                         MstcnlOrderAttachment.objects.using('mstcnl').create(
    #                             attachment_id=attachment.get("attachment_id"),
    #                             order_id=sale_order_id,
    #                             order_type_id=attachment.get("order_type", {}).get("name"),
    #                             attachment_name=attachment.get("attachment_name"),
    #                             attachment_path=attachment.get("attachment_path"),
    #                             # file_size=attachment.get("file_size", 0),
    #                             created_at=timezone.now(),
    #                             updated_at=timezone.now(),
    #                         )
    #                         logger.info(" Order Attachments items created in mstcnl DB")
    #                     except Exception as e:
    #                         logger.warning(f"❌ Failed to replicate OrderAttachment to mstcnl DB: {e}")

    #             #  Shipments: only if present and has shipment_id
    #             if order_shipments_data and isinstance(order_shipments_data, dict) and order_shipments_data.get("shipment_id"):
    #                 try:
    #                     MstcnlOrderShipment.objects.using('mstcnl').create(
    #                         shipment_id=order_shipments_data.get("shipment_id"),
    #                         order_id=sale_order_id,
    #                         order_type_id=order_shipments_data.get("order_type", {}).get("name"),
    #                         shipping_mode_id=order_shipments_data.get("shipping_mode"),
    #                         shipping_company_id=order_shipments_data.get("shipping_company"),
    #                         shipping_tracking_no=order_shipments_data.get("shipping_tracking_no"),
    #                         shipping_date=order_shipments_data.get("shipping_date"),
    #                         # expected_delivery_date=None,  # Not in payload
    #                         destination=order_shipments_data.get("destination"),
    #                         created_at=timezone.now(),
    #                         updated_at=timezone.now(),
    #                     )
    #                     logger.info(" Order Shipments items created in mstcnl DB")
    #                 except Exception as e:
    #                     logger.warning(f"❌ Failed to replicate OrderShipment to mstcnl DB: {e}")
                        
    #             # Add a 2-second delay before deletion
    #             time.sleep(3)

    #             #  Delete from default DB
    #             try:
    #                 set_db('default')
    #                 using_db = 'default'

    #                 # Delete sale order from default DB if exists
    #                 #print("We are in the delete mode...")
    #                 SaleOrderItems.objects.using('default').filter(sale_order_id=sale_order_id).delete()
    #                 OrderAttachments.objects.using('default').filter(order_id=sale_order_id).delete()
    #                 OrderShipments.objects.using('default').filter(order_id=sale_order_id).delete()
    #                 SaleOrder.objects.using('default').filter(sale_order_id=sale_order_id).delete()
    #                 #print("After delete mode...")

    #             except Exception as delete_error:
    #                 logger.warning(f"⚠️ Failed to delete original records from default DB: {delete_error}")

    #             return build_response(1, "Sale Order and related data replicated to mstcnl DB", {}, status.HTTP_201_CREATED)
    #         except Exception as e:
    #             logger.error(f"❌ Failed to replicate SaleOrder to mstcnl DB: {e}")
    #             return build_response(0, "Replication failed", {}, status.HTTP_500_INTERNAL_SERVER_ERROR)


    #     # ---------------------- VALIDATION ----------------------------------#
        
      
    #     set_db('default')
    #     using_db = 'default'
    #     order_error, item_error, attachment_error, shipments_error, custom_error = [], [], [], [], []

    #     if sale_order_data:
    #         order_error = validate_payload_data(self, sale_order_data, SaleOrderSerializer, using=using_db)
    #         validate_order_type(sale_order_data, order_error, OrderTypes, look_up='order_type')

    #     if sale_order_items_data:
    #         item_error = validate_multiple_data(self, sale_order_items_data, SaleOrderItemsSerializer, ['sale_order_id'], using_db=using_db)

    #     if order_attachments_data:
    #         attachment_error = validate_multiple_data(self, order_attachments_data, OrderAttachmentsSerializer, ['order_id', 'order_type_id'], using_db=using_db)

    #     if order_shipments_data:
    #         if len(order_shipments_data) > 1:
    #             shipments_error = validate_multiple_data(self, [order_shipments_data], OrderShipmentsSerializer, ['order_id', 'order_type_id'], using_db=using_db)
    #         else:
    #             order_shipments_data = {}
    #             shipments_error = []

    #     if custom_fields_data:
    #         if len(custom_fields_data) > 1:
    #             custom_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'], using_db=using_db)
    #         else:
    #             custom_error = []
            
    #     if not sale_order_data or not sale_order_items_data:
    #         logger.error("Sale order and sale order items and CustomFields are mandatory but not provided.")
    #         return build_response(0, "Sale order and sale order items & CustomFields are mandatory", [], status.HTTP_400_BAD_REQUEST)

    #     errors = {}
    #     if order_error: errors["sale_order"] = order_error
    #     if item_error: errors["sale_order_items"] = item_error
    #     if attachment_error: errors["order_attachments"] = attachment_error
    #     if shipments_error: errors["order_shipments"] = shipments_error
    #     if custom_error: errors["custom_field_values"] = custom_error

    #     if errors:
    #         return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

    #     # ---------------------- D A T A   C R E A T I O N ----------------------------#
    #     new_sale_order_data = generic_data_creation(self, [sale_order_data], SaleOrderSerializer, using=using_db)[0]
    #     sale_order_id = new_sale_order_data.get("sale_order_id", None)
    #     logger.info(f'SaleOrder - created in {using_db} DB')

    #     if sale_order_id:
    #         update_fields = {'sale_order_id': sale_order_id}
    #         items_data = generic_data_creation(self, sale_order_items_data, SaleOrderItemsSerializer, update_fields, using=using_db)
    #         logger.info(f'SaleOrderItems - created in {using_db} DB')

    #     order_type_val = sale_order_data.get('order_type')
    #     order_type = get_object_or_none(OrderTypes, name=order_type_val)
    #     type_id = order_type.order_type_id

    #     update_fields = {'order_id': sale_order_id, 'order_type_id': type_id}
    #     if order_attachments_data:
    #         order_attachments = generic_data_creation(self, order_attachments_data, OrderAttachmentsSerializer, update_fields, using=using_db)
    #         logger.info(f'OrderAttachments - created in {using_db} DB')
    #     else:
    #         order_attachments = []

    #     if order_shipments_data:
    #         order_shipments = generic_data_creation(self, [order_shipments_data], OrderShipmentsSerializer, update_fields, using=using_db)
    #         logger.info(f'OrderShipments - created in {using_db} DB')
    #     else:
    #         order_shipments = []

    #     if custom_fields_data:
    #         update_fields = {'custom_id': sale_order_id}
    #         custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, update_fields, using=using_db)
    #         logger.info(f'CustomFieldValues - created in {using_db} DB')

    #     # -------------------- Inventory Blocking ----------------------------------
    #     if sale_order_data.get("sale_estimate", "").lower() != "yes":
    #         block_duration = InventoryBlockConfig.objects.using(using_db).filter(product_id__isnull=True).first()
    #         block_duration_hours = getattr(block_duration, 'block_duration_hours', 24)
    #         expiration_time = timezone.now() + timedelta(hours=block_duration_hours)

    #         blocked_inventory_data = []
    #         for item in sale_order_items_data:
    #             product_id = item.get("product_id")
    #             ordered_qty = item.get("quantity")
    #             product = Products.objects.using(using_db).filter(product_id=product_id).first()

    #             if product:
    #                 if product.balance >= ordered_qty:
    #                     product.balance = F('balance') - ordered_qty
    #                     product.save(using=using_db, update_fields=['balance'])

    #                 blocked_inventory_data.append(BlockedInventory(
    #                     sale_order_id=SaleOrder.objects.using(using_db).get(sale_order_id=sale_order_id),
    #                     product_id=Products.objects.using(using_db).get(product_id=product_id),
    #                     blocked_qty=ordered_qty,
    #                     expiration_time=expiration_time
    #                 ))
    #             else:
    #                 return build_response(0, f"Product with ID {product_id} not found.", [], status.HTTP_404_NOT_FOUND)

    #         BlockedInventory.objects.using(using_db).bulk_create(blocked_inventory_data, ignore_conflicts=True)
    #         logger.info("Inventory blocked for sale order %s.", sale_order_id)

    #     # ---------------------- R E S P O N S E ----------------------------#
    #     # -------------------- AUTO WHATSAPP (NON-BLOCKING) --------------------
    #     whatsapp_result = try_send_sale_order_whatsapp(request, sale_order_id)

    #     custom_data = {
    #         "sale_order": new_sale_order_data,
    #         "sale_order_items": items_data,
    #         "order_attachments": order_attachments,
    #         "order_shipments": order_shipments,
    #         "custom_field_values": custom_fields_data,
    #         "whatsapp": whatsapp_result
    #     }
        
    #     sale_order_no = sale_order_data.get("order_no")
        
    #     # Log the Create
    #     log_user_action(
    #         using_db,
    #         request.user,
    #         "CREATE",
    #         "Sale Order",
    #         sale_order_id,
    #         f"Sale Order Created on {sale_order_no} by {request.user.username}"
    #     )
    #     return build_response(1, "Sale Order created successfully", custom_data, status.HTTP_201_CREATED)


#--------------------------------------------------------
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        given_data = request.data

        # Extract payload
        sale_order_data = given_data.pop('sale_order', None)
        sale_order_items_data = given_data.pop('sale_order_items', None)
        order_attachments_data = given_data.pop('order_attachments', None)
        order_shipments_data = given_data.pop('order_shipments', None)
        custom_fields_data = given_data.pop('custom_field_values', None)

        # ---------------- CLEAN EMPTY SALE ORDER ITEMS ---------------- #
        sale_order_items_data = [
            item for item in sale_order_items_data
            if item.get("product_id") and item.get("quantity")
        ]
        # -------------------------------------------------------------- #

        sale_type_name = sale_order_data.get("sale_type", {}).get("name")
        flow_status_name = sale_order_data.get("flow_status", {}).get("flow_status_name")
        is_mstcnl = sale_type_name == "Other" and flow_status_name == "Completed"

        # ---------------------- VALIDATION ----------------------------------#
        set_db('default')
        using_db = 'default'

        order_error, item_error, attachment_error, shipments_error, custom_error = [], [], [], [], []

        if sale_order_data:
            order_error = validate_payload_data(self, sale_order_data, SaleOrderSerializer, using=using_db)
            validate_order_type(sale_order_data, order_error, OrderTypes, look_up='order_type')

        if sale_order_items_data:
            item_error = validate_multiple_data(
                self, sale_order_items_data,
                SaleOrderItemsSerializer,
                ['sale_order_id'], using_db=using_db
            )

        if order_attachments_data:
            attachment_error = validate_multiple_data(
                self, order_attachments_data,
                OrderAttachmentsSerializer,
                ['order_id', 'order_type_id'], using_db=using_db
            )

        if order_shipments_data:
            if len(order_shipments_data) > 1:
                shipments_error = validate_multiple_data(
                    self, [order_shipments_data],
                    OrderShipmentsSerializer,
                    ['order_id', 'order_type_id'], using_db=using_db
                )
            else:
                order_shipments_data = {}
                shipments_error = []

        if custom_fields_data:
            if len(custom_fields_data) > 1:
                custom_error = validate_multiple_data(
                    self, custom_fields_data,
                    CustomFieldValueSerializer,
                    ['custom_id'], using_db=using_db
                )
            else:
                custom_error = []

        if not sale_order_data or not sale_order_items_data:
            return build_response(
                0,
                "Sale order and sale order items & CustomFields are mandatory",
                [],
                status.HTTP_400_BAD_REQUEST
            )

        errors = {}
        if order_error: errors["sale_order"] = order_error
        if item_error: errors["sale_order_items"] = item_error
        if attachment_error: errors["order_attachments"] = attachment_error
        if shipments_error: errors["order_shipments"] = shipments_error
        if custom_error: errors["custom_field_values"] = custom_error

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- DATA CREATION ----------------------------#
        new_sale_order_data = generic_data_creation(
            self, [sale_order_data],
            SaleOrderSerializer,
            using=using_db
        )[0]

        sale_order_id = new_sale_order_data.get("sale_order_id")
        logger.info(f'SaleOrder - created in {using_db} DB')

        if sale_order_id:
            update_fields = {'sale_order_id': sale_order_id}
            items_data = generic_data_creation(
                self,
                sale_order_items_data,
                SaleOrderItemsSerializer,
                update_fields,
                using=using_db
            )
            logger.info(f'SaleOrderItems - created in {using_db} DB')

        # ===================== QUANTITY SPLIT LOGIC (ADDED) ===================== #
        for item in sale_order_items_data:
            product_id = item.get("product_id")
            ordered_qty = int(item.get("quantity", 0))

            product = Products.objects.using(using_db).filter(product_id=product_id).first()
            if not product:
                continue

            available_qty = min(product.balance or 0, ordered_qty)
            production_qty = ordered_qty - available_qty

            SaleOrderItems.objects.using(using_db).filter(
                sale_order_id=sale_order_id,
                product_id=product_id
            ).update(
                available_qty=available_qty,
                production_qty=production_qty
            )
        # ======================================================================= #

        order_type_val = sale_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        update_fields = {'order_id': sale_order_id, 'order_type_id': type_id}

        if order_attachments_data:
            order_attachments = generic_data_creation(
                self, order_attachments_data,
                OrderAttachmentsSerializer,
                update_fields,
                using=using_db
            )
        else:
            order_attachments = []

        if order_shipments_data:
            order_shipments = generic_data_creation(
                self, [order_shipments_data],
                OrderShipmentsSerializer,
                update_fields,
                using=using_db
            )
        else:
            order_shipments = []

        if custom_fields_data:
            update_fields = {'custom_id': sale_order_id}
            custom_fields_data = generic_data_creation(
                self, custom_fields_data,
                CustomFieldValueSerializer,
                update_fields,
                using=using_db
            )

        # -------------------- Inventory Blocking (UPDATED) --------------------
        if sale_order_data.get("sale_estimate", "").lower() != "yes":
            block_duration = InventoryBlockConfig.objects.using(using_db).filter(product_id__isnull=True).first()
            block_duration_hours = getattr(block_duration, 'block_duration_hours', 24)
            expiration_time = timezone.now() + timedelta(hours=block_duration_hours)

            blocked_inventory_data = []

            for item in sale_order_items_data:
                product_id = item.get("product_id")

                ordered_qty = SaleOrderItems.objects.using(using_db).filter(
                    sale_order_id=sale_order_id,
                    product_id=product_id
                ).values_list("available_qty", flat=True).first() or 0

                product = Products.objects.using(using_db).filter(product_id=product_id).first()
                if not product:
                    continue

                if ordered_qty > 0:
                    product.balance = F('balance') - ordered_qty
                    product.save(using=using_db, update_fields=['balance'])

                    blocked_inventory_data.append(
                        BlockedInventory(
                            sale_order_id=SaleOrder.objects.using(using_db).get(sale_order_id=sale_order_id),
                            product_id=Products.objects.using(using_db).get(product_id=product_id),
                            blocked_qty=ordered_qty,
                            expiration_time=expiration_time
                        )
                    )

            BlockedInventory.objects.using(using_db).bulk_create(blocked_inventory_data, ignore_conflicts=True)

        # ---------------------- RESPONSE ----------------------------#
        whatsapp_result = try_send_sale_order_whatsapp(request, sale_order_id)

        custom_data = {
            "sale_order": new_sale_order_data,
            "sale_order_items": items_data,
            "order_attachments": order_attachments,
            "order_shipments": order_shipments,
            "custom_field_values": custom_fields_data,
            "whatsapp": whatsapp_result
        }

        sale_order_no = sale_order_data.get("order_no")

        log_user_action(
            using_db,
            request.user,
            "CREATE",
            "Sale Order",
            sale_order_id,
            f"Sale Order Created on {sale_order_no} by {request.user.username}"
        )

        return build_response(1, "Sale Order created successfully", custom_data, status.HTTP_201_CREATED)


#---------------------------------------------------------

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        # ----------------------------------- C H E C K  D A T A B A S E -----------------------------#
        db_to_use = None
        errors = {}
        try:
            # Check if sale_order_id exists in the mstcnl database
            MstcnlSaleOrder.objects.using('mstcnl').get(sale_order_id=pk)
            return build_response(
                0,
                "Update is not allowed, please contact Product team.",
                errors,
                status.HTTP_400_BAD_REQUEST
            )
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
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Vlidated SaleOrder Data
        sale_order_data = given_data.pop('sale_order', None)  # parent_data
        if sale_order_data:
            sale_order_data['sale_order_id'] = pk
            order_error = validate_multiple_data(
                self, [sale_order_data], SaleOrderSerializer, ['order_no'])
            # validate the 'order_type' in 'sale_order' data
            validate_order_type(sale_order_data, order_error,OrderTypes, look_up='order_type')

        # Vlidated SaleOrderItems Data
        sale_order_items_data = given_data.pop('sale_order_items', None)
        
        # ------------------ IMPORTANT NEW LOGIC ------------------ #
        # Filter out empty UI rows (only keep rows with real product)
        if sale_order_items_data:
            sale_order_items_data = [
                item for item in sale_order_items_data
                if item.get("product_id") and item.get("quantity")
            ]
            
        if sale_order_items_data:
            exclude_fields = ['sale_order_id']
            item_error = validate_put_method_data(self, sale_order_items_data, SaleOrderItemsSerializer,
                                                  exclude_fields, SaleOrderItems, current_model_pk_field='sale_order_item_id')

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id', 'order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(
                self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(
                self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
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
        if not sale_order_data or not sale_order_items_data:
            logger.error("Sale order and sale order items & CustomFeilds are mandatory but not provided.")
            return build_response(0, "Sale order and sale order items & CustomFeilds are mandatory", [], status.HTTP_400_BAD_REQUEST)

        
        if order_error:
            errors["sale_order"] = order_error
        if item_error:
            errors["sale_order_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if custom_field_values_error:
            errors['custom_field_values'] = custom_field_values_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#

        # update SaleOrder
        if sale_order_data:
            update_fields = []  # No need to update any fields
            saleorder_data = update_multi_instances(self, pk, [sale_order_data], SaleOrder, SaleOrderSerializer,
                                                    update_fields, main_model_related_field='sale_order_id', current_model_pk_field='sale_order_id')

        # Update the 'sale_order_items'
        update_fields = {'sale_order_id': pk}
        items_data = update_multi_instances(self, pk, sale_order_items_data, SaleOrderItems, SaleOrderItemsSerializer,
                                            update_fields, main_model_related_field='sale_order_id', current_model_pk_field='sale_order_item_id')

        # Get 'order_type_id' from 'OrderTypes' model
        order_type_val = sale_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id': pk, 'order_type_id': type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer,
                                                 update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id')

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer,
                                               update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id')
        
        # Update CustomFieldValues Data
        if custom_field_values_data:
            custom_field_values_data = update_multi_instances(self, pk, custom_field_values_data, CustomFieldValue, CustomFieldValueSerializer, {}, main_model_related_field='custom_id', current_model_pk_field='custom_field_value_id')

        # whatsapp_result = try_send_sale_order_whatsapp(request, pk)
        
        custom_data = {
            "sale_order": saleorder_data[0] if saleorder_data else {},
            "sale_order_items": items_data if items_data else [],
            "order_attachments": attachment_data if attachment_data else [],
            "order_shipments": shipment_data[0] if shipment_data else {},
            "custom_field_values": custom_field_values_data if custom_field_values_data else []  # Add custom field values to response
            # "whatsapp": whatsapp_result
        }
        sale_order_no = sale_order_data.get("order_no")
        # Log the Create
        log_user_action(
            db_to_use,
            request.user,
            "UPDATE",
            "Sale Order",
            pk,
            f"{sale_order_no} Sale Order Updated by {request.user.username}"
        )

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)


    def patch(self, request, pk, format=None):
        # Determine which DB the sale_order belongs to
        if SaleOrder.objects.using('default').filter(pk=pk).exists():
            db_alias = 'default'
        elif MstcnlSaleOrder.objects.using('mstcnl').filter(pk=pk).exists():
            db_alias = 'mstcnl'
        else:
            return build_response(0, f"sale_order_id {pk} not found in either DB", [], status.HTTP_400_BAD_REQUEST)

        # Set DB context
        set_db(db_alias)

        sale_order = self.get_object(pk)
        # #print("Sale Order data : ", sale_order)
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

        #  Remove selected items if provided
        sale_order_items_data = request.data.pop("sale_order_items", None)

        serializer = SaleOrderOptionsSerializer(sale_order, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            if sale_order_items_data is not None:
                # from sales.models import SaleOrderItems

                # Delete only the selected items
                selected_item_ids = [item.get('sale_order_item_id') for item in sale_order_items_data]
                SaleOrderItems.objects.using(db_alias).filter(
                    pk__in=selected_item_ids, sale_order_id=sale_order.pk
                ).delete()

                remaining_items = SaleOrderItems.objects.using(db_alias).filter(sale_order_id=sale_order.pk)

                item_value_total = 0
                tax_amount_total = 0
                product_discount_total = 0

                for item in remaining_items:
                    try:
                        quantity = float(item.quantity or 0)
                        rate = float(item.rate or 0)
                        discount = float(item.discount or 0)
                        cgst = float(item.cgst or 0)
                        sgst = float(item.sgst or 0)
                        igst = float(item.igst or 0)

                        item_value = quantity * rate
                        item_discount_amount = (item_value * discount) / 100
                        tax_total = cgst + sgst + igst

                        item_value_total += item_value
                        tax_amount_total += tax_total
                        product_discount_total += item_discount_amount
                    except Exception as e:
                        print(f"Error in item {item.pk}: {e}")

                overall_discount = float(sale_order.dis_amt or 0)
                cess_amount = float(sale_order.cess_amount or 0)

                # Final total calculation
                total_amount = item_value_total - product_discount_total - overall_discount + tax_amount_total + cess_amount

                # Round final amount (optional to 2 decimal places)
                rounded_total_amount = round(total_amount, 2)

                #  Save updated values
                sale_order.total_amount = rounded_total_amount
                sale_order.tax_amount = tax_amount_total
                sale_order.dis_amt = overall_discount  # unchanged
                sale_order.save() 
                
                # Log the Create
                log_user_action(
                    db_alias,
                    request.user,
                    "PATCH",
                    "Sale Order",
                    pk,
                    f"{sale_order.order_no} - Sale Order Record Partially Updated by {request.user.username}"
                )         

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

    # def get(self, request, *args, **kwargs):
    #     if "pk" in kwargs:
    #         result =  validate_input_pk(self,kwargs['pk'])
    #         return result if result else self.retrieve(self, request, *args, **kwargs) 
    #     try:
    #         # Check if the 'records_all' filter is set in the query params
    #         records_all = request.query_params.get("records_all", "false").lower() == "true"
    #         records_mstcnl = request.query_params.get("records_mstcnl", "false").lower() == "true"
            
    #         logger.info(f"Fetching records_all: {records_all}")
            
    #         summary = request.query_params.get("summary", "false").lower() == "true"
    #         if summary:
    #             logger.info("Retrieving sale invoice order summary")
    #             saleinvoiceorder = SaleInvoiceOrders.objects.all().order_by('is_deleted', '-created_at')
    #             data = SaleInvoiceOrderOptionsSerializer.get_sale_invoice_order_summary(saleinvoiceorder)
    #             return build_response(len(data), "Success", data, status.HTTP_200_OK)
             
    #         logger.info("Retrieving all sale invoice orders")

    #         page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
    #         limit = int(request.query_params.get('limit', 10)) 

    #         queryset = SaleInvoiceOrders.objects.all().order_by('is_deleted', '-created_at')

    #         if records_all:
    #             logger.info("Fetching sale order summary from both mstcnl and default databases")

    #             # DB: mstcnl
    #             base_queryset_mstcnl = MstcnlSaleInvoiceOrder.objects.using('mstcnl').all().order_by('is_deleted', '-created_at')
    #             filterset_mstcnl = MstcnlSaleInvoiceFilter(request.GET, queryset=base_queryset_mstcnl)
    #             if filterset_mstcnl.is_valid():
    #                 saleorders_mstcnl = filterset_mstcnl.qs
    #             else:
    #                 saleorders_mstcnl = base_queryset_mstcnl

    #             # DB: default
    #             base_queryset_devcnl = SaleInvoiceOrders.objects.using('default').all().order_by('is_deleted', '-created_at')
    #             filterset_devcnl = SaleInvoiceOrdersFilter(request.GET, queryset=base_queryset_devcnl)
    #             if filterset_devcnl.is_valid():
    #                 saleorders_devcnl = filterset_devcnl.qs
    #             else:
    #                 saleorders_devcnl = base_queryset_devcnl

    #             # Combine both
    #             combined_queryset = list(chain(saleorders_mstcnl, saleorders_devcnl))
    #             total_count = len(combined_queryset)

    #             # Manual pagination on combined list
    #             start_index = (page - 1) * limit
    #             end_index = start_index + limit
    #             paginated_results = combined_queryset[start_index:end_index]

    #             # Separate the paginated slice into two: mstcnl & devcnl
    #             paginated_mstcnl = [obj for obj in paginated_results if isinstance(obj, MstcnlSaleInvoiceOrder)]
    #             paginated_devcnl = [obj for obj in paginated_results if isinstance(obj, SaleInvoiceOrders)]

    #             # Serialize each with its correct serializer
    #             serializer_mstcnl = MstcnlSaleInvoiceSerializer(paginated_mstcnl, many=True)
    #             serializer_devcnl = SaleInvoiceOrdersSerializer(paginated_devcnl, many=True)

    #             # Combine results
    #             final_results = serializer_mstcnl.data + serializer_devcnl.data

    #             return filter_response(
    #                 total_count,
    #                 "Success",
    #                 final_results,
    #                 page,
    #                 limit,
    #                 total_count,
    #                 status.HTTP_200_OK
    #             )
    #         elif records_mstcnl:
    #             logger.info("Fetching sale orders only from mstcnl database")

    #             base_queryset_mstcnl = MstcnlSaleInvoiceOrder.objects.using('mstcnl').all().order_by('is_deleted', '-created_at')

    #             filterset_mstcnl = MstcnlSaleInvoiceFilter(request.GET, queryset=base_queryset_mstcnl)
    #             if filterset_mstcnl.is_valid():
    #                 saleorders_mstcnl = filterset_mstcnl.qs
    #             else:
    #                 saleorders_mstcnl = base_queryset_mstcnl

    #             total_count = saleorders_mstcnl.count()
    #             start_index = (page - 1) * limit
    #             end_index = start_index + limit
    #             paginated_results = saleorders_mstcnl[start_index:end_index]

    #             serializer_mstcnl = MstcnlSaleInvoiceSerializer(paginated_results, many=True)

    #             return filter_response(
    #                 total_count,
    #                 "Success",
    #                 serializer_mstcnl.data,
    #                 page,
    #                 limit,
    #                 total_count,
    #                 status.HTTP_200_OK
    #             )

    #         else:
    #             logger.info("Fetching sale orders only from devcnl")
    #             # Only query from the 'devcnl' database
    #             # queryset = SaleInvoiceOrders.objects.using('default').all().order_by('is_deleted', '-created_at')
                
    #             # Get cancelled status IDs
    #             canceled_status_ids = list(OrderStatuses.objects.filter(
    #             status_name__in=['Cancelled']
    #             ).values_list('order_status_id', flat=True))
            
    #             # queryset = SaleInvoiceOrders.objects.all().order_by('-invoice_date')
    #             queryset = SaleInvoiceOrders.objects.exclude(
    #             order_status_id__in=canceled_status_ids
    #                                ).order_by('is_deleted', '-created_at')
        
    #             total_count = SaleInvoiceOrders.objects.count()
    #             # Apply filters manually
    #             if request.query_params:
    #                 filterset = SaleInvoiceOrdersFilter(request.GET, queryset=queryset)
    #                 if filterset.is_valid():
    #                     queryset = filterset.qs 
                        
    #             total_count = queryset.count()
    #             paginated_results = queryset[(page - 1) * limit: page * limit]

    #         # total_count = SaleInvoiceOrders.objects.count()

    #         serializer = SaleInvoiceOrderOptionsSerializer(paginated_results, many=True)
    #         logger.info("sale order invoice data retrieved successfully.")
    #         # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
    #         return filter_response(total_count,"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    #     except Exception as e:
    #         logger.error(f"An unexpected error occurred: {str(e)}")
    #         return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result =  validate_input_pk(self,kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs) 
        try:
            records_all = request.query_params.get("records_all", "false").lower() == "true"
            records_mstcnl = request.query_params.get("records_mstcnl", "false").lower() == "true"
            
            logger.info(f"Fetching records_all: {records_all}")
            
            # ===================== SALE REGISTER =====================
            # Handle both ?sale_register and ?sale_register=true
            sale_register_param = request.query_params.get("sale_register", None)
            sale_register = sale_register_param is not None and sale_register_param.lower() != "false"
            if sale_register:
                return self.get_sale_register(request)
            
            summary = request.query_params.get("summary", "false").lower() == "true"

            if summary:
                saleinvoiceorder = SaleInvoiceOrders.objects.all().order_by('is_deleted', '-created_at')

                # ✅ Dynamically fetch the IDs
                canceled_status_ids = list(OrderStatuses.objects.filter(
                    status_name__in=['Cancelled']
                ).values_list('order_status_id', flat=True))

                completed_status_id = OrderStatuses.objects.filter(
                    status_name="Completed"
                ).values_list("order_status_id", flat=True).first()

                # ✅ Exclude either Cancelled OR (bill_type=Others AND status=Completed)
                if completed_status_id:
                    exclude_q = Q(order_status_id__in=canceled_status_ids) | (
                        Q(bill_type__iexact="Others") & Q(order_status_id=completed_status_id)
                    )
                else:
                    exclude_q = Q(order_status_id__in=canceled_status_ids)

                saleinvoiceorder = saleinvoiceorder.exclude(exclude_q) 

                data = SaleInvoiceOrderOptionsSerializer.get_sale_invoice_order_summary(saleinvoiceorder)

                total_count = len(data)  # total after summary processing
                page = int(request.query_params.get('page', 1))
                limit = int(request.query_params.get('limit', 10))

                # manual pagination on summary data
                start_index = (page - 1) * limit
                end_index = start_index + limit
                paginated_data = data[start_index:end_index]

                return filter_response(
                    total_count,
                    "Success",
                    paginated_data,
                    page,
                    limit,
                    total_count,
                    status.HTTP_200_OK
                )
            
            # if summary:
            #     saleinvoiceorder = SaleInvoiceOrders.objects.all().order_by('is_deleted', '-created_at')

            #     # ✅ Dynamically fetch the IDs
            #     canceled_status_ids = list(OrderStatuses.objects.filter(
            #         status_name__in=['Cancelled']
            #     ).values_list('order_status_id', flat=True))

            #     completed_status_id = OrderStatuses.objects.filter(
            #         status_name="Completed"
            #     ).values_list("order_status_id", flat=True).first()

            #     # ✅ Exclude either Cancelled OR (bill_type=Others AND status=Completed)
            #     if completed_status_id:
            #         exclude_q = Q(order_status_id__in=canceled_status_ids) | (
            #             Q(bill_type__iexact="Others") & Q(order_status_id=completed_status_id)
            #         )
            #     else:
            #         exclude_q = Q(order_status_id__in=canceled_status_ids)

            #     saleinvoiceorder = saleinvoiceorder.exclude(exclude_q)

            #     # 🔹 APPLY SEARCH HERE BEFORE SERIALIZATION
            #     search_value = request.query_params.get('s')
            #     if search_value:
            #         filter_set = SaleInvoiceOrdersFilter(data={'s': search_value})
            #         saleinvoiceorder = filter_by_search(saleinvoiceorder, filter_set, search_value)

            #     data = SaleInvoiceOrderOptionsSerializer.get_sale_invoice_order_summary(saleinvoiceorder)

            #     total_count = len(data)  # total after summary processing
            #     page = int(request.query_params.get('page', 1))
            #     limit = int(request.query_params.get('limit', 10))

            #     # manual pagination on summary data
            #     start_index = (page - 1) * limit
            #     end_index = start_index + limit
            #     paginated_data = data[start_index:end_index]

            #     return filter_response(
            #         total_count,
            #         "Success",
            #         paginated_data,
            #         page,
            #         limit,
            #         total_count,
            #         status.HTTP_200_OK
            #     )

            
            # from django_filters.rest_framework import DjangoFilterBackend

                        # if records_all:
            #     logger.info("Fetching sale order summary from both mstcnl and default databases")

            #     # DB: mstcnl
            #     base_queryset_mstcnl = MstcnlSaleInvoiceOrder.objects.using('mstcnl').all().order_by('-created_at')
            #     filterset_mstcnl = MstcnlSaleInvoiceFilter(request.GET, queryset=base_queryset_mstcnl)
            #     if filterset_mstcnl.is_valid():
            #         saleorders_mstcnl = filterset_mstcnl.qs
            #     else:
            #         saleorders_mstcnl = base_queryset_mstcnl

            #     # DB: default
            #     base_queryset_devcnl = SaleInvoiceOrders.objects.using('default').all().order_by('is_deleted', '-created_at')
            #     filterset_devcnl = SaleInvoiceOrdersFilter(request.GET, queryset=base_queryset_devcnl)
            #     if filterset_devcnl.is_valid():
            #         saleorders_devcnl = filterset_devcnl.qs
            #     else:
            #         saleorders_devcnl = base_queryset_devcnl

            #     # Combine both
            #     combined_queryset = list(chain(saleorders_mstcnl, saleorders_devcnl))
            #     page = int(request.query_params.get('page', 1))
            #     limit = int(request.query_params.get('limit', 10))
            #     total_count = len(combined_queryset)  # ✅ Correct: filtered combined count

            #     # Manual pagination on combined list
            #     start_index = (page - 1) * limit
            #     end_index = start_index + limit
            #     paginated_results = combined_queryset[start_index:end_index]

            #     # Separate the paginated slice into two: mstcnl & devcnl
            #     paginated_mstcnl = [obj for obj in paginated_results if isinstance(obj, MstcnlSaleInvoiceOrder)]
            #     paginated_devcnl = [obj for obj in paginated_results if isinstance(obj, SaleInvoiceOrders)]

            #     # Serialize each with its correct serializer
            #     serializer_mstcnl = MstcnlSaleInvoiceSerializer(paginated_mstcnl, many=True)
            #     serializer_devcnl = SaleInvoiceOrdersSerializer(paginated_devcnl, many=True)

            #     # Combine results
            #     final_results = serializer_mstcnl.data + serializer_devcnl.data

            #     return filter_response(
            #         total_count,
            #         "Success",
            #         final_results,
            #         page,
            #         limit,
            #         total_count,
            #         status.HTTP_200_OK
            #     )
            if records_all:
                logger.info("Fetching ALL sale invoice order summary from both mstcnl and default databases (no pagination)")

                # Create copies of GET params without pagination for filtering
                filter_params = request.GET.copy()
                if 'page' in filter_params:
                    del filter_params['page']
                if 'limit' in filter_params:
                    del filter_params['limit']

                # DB: mstcnl - apply base ordering and filtering
                base_queryset_mstcnl = MstcnlSaleInvoiceOrder.objects.using('mstcnl').all().order_by('-created_at')
                filterset_mstcnl = MstcnlSaleInvoiceFilter(filter_params, queryset=base_queryset_mstcnl)
                if filterset_mstcnl.is_valid():
                    saleorders_mstcnl = filterset_mstcnl.qs
                else:
                    saleorders_mstcnl = base_queryset_mstcnl

                # DB: default - apply base ordering and filtering
                base_queryset_devcnl = SaleInvoiceOrders.objects.using('default').all().order_by('is_deleted', '-created_at')
                filterset_devcnl = SaleInvoiceOrdersFilter(filter_params, queryset=base_queryset_devcnl)
                if filterset_devcnl.is_valid():
                    saleorders_devcnl = filterset_devcnl.qs
                else:
                    saleorders_devcnl = base_queryset_devcnl

                # Get all records from both databases (no pagination)
                all_mstcnl_records = saleorders_mstcnl
                all_devcnl_records = saleorders_devcnl

                # Serialize all records
                serializer_mstcnl = MstcnlSaleInvoiceSerializer(all_mstcnl_records, many=True)
                serializer_devcnl = SaleInvoiceOrdersSerializer(all_devcnl_records, many=True)

                # Combine results
                final_results = serializer_mstcnl.data + serializer_devcnl.data
                total_count = len(final_results)

                # Return ALL records without pagination metadata
                return Response({
                    "count": total_count,
                    "message": "Success",
                    "data": final_results,
                    "totalCount": total_count
                }, status=status.HTTP_200_OK)

            elif records_mstcnl:
                logger.info("Fetching sale orders only from mstcnl database")

                base_queryset_mstcnl = MstcnlSaleInvoiceOrder.objects.using('mstcnl').all().order_by('-created_at')
                filterset_mstcnl = MstcnlSaleInvoiceFilter(request.GET, queryset=base_queryset_mstcnl)
                if filterset_mstcnl.is_valid():
                    saleorders_mstcnl = filterset_mstcnl.qs
                else:
                    saleorders_mstcnl = base_queryset_mstcnl

                page = int(request.query_params.get('page', 1))
                limit = int(request.query_params.get('limit', 10))
                total_count = saleorders_mstcnl.count()  # ✅ Correct: filtered count
                start_index = (page - 1) * limit
                end_index = start_index + limit
                paginated_results = saleorders_mstcnl[start_index:end_index]

                serializer_mstcnl = MstcnlSaleInvoiceSerializer(paginated_results, many=True)

                return filter_response(
                    total_count,
                    "Success",
                    serializer_mstcnl.data,
                    page,
                    limit,
                    total_count,
                    status.HTTP_200_OK
                )

            else:
                logger.info("Fetching sale orders only from devcnl")

                # ✅ Dynamically fetch the IDs
                # completed_status_id = OrderStatuses.objects.filter(status_name="Completed").first()

                canceled_status_ids = list(OrderStatuses.objects.filter(
                    status_name__in=['Cancelled']
                ).values_list('order_status_id', flat=True))

                queryset = SaleInvoiceOrders.objects.exclude(
                    order_status_id__in=canceled_status_ids
                ).order_by('is_deleted', '-created_at')
                
                # # ✅ Exclude if both found
                # if completed_status_id:
                #     queryset = queryset.exclude(
                #         bill_type="Others",
                #         order_status_id=completed_status_id
                #     )

                # Apply filters manually
                if request.query_params:
                    filterset = SaleInvoiceOrdersFilter(request.GET, queryset=queryset)
                    if filterset.is_valid():
                        queryset = filterset.qs 

                page = int(request.query_params.get('page', 1))
                limit = int(request.query_params.get('limit', 10))
                total_count = queryset.count()  # ✅ Correct: filtered count
                paginated_results = queryset[(page - 1) * limit: page * limit]

                serializer = SaleInvoiceOrderOptionsSerializer(paginated_results, many=True)
                logger.info("sale order invoice data retrieved successfully.")

                return filter_response(total_count,"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # ===================== SALE REGISTER API =====================
    def get_sale_register(self, request):
        """
        Sale Register API for reporting.
        
        Query Parameters:
        - from_date: Start date (YYYY-MM-DD)
        - to_date: End date (YYYY-MM-DD)
        - register_type: general | detailed | tax_wise | cancelled | product_group_wise | hsn_wise | daily_sales_summary | monthly_sales_summary
        - voucher_type: CASH | CREDIT | OTHERS (optional, filters by bill_type)
        - customer: Customer name search
        - page, limit: Pagination
        
        Response varies based on register_type:
        - general: Invoice-level summary grouped by voucher type
        - detailed: Product-level details (Date, Doc No, Product Name, Qty, Unit, Rate, Net Amount, Amount)
        - cancelled: Only cancelled invoices
        - daily_sales_summary: Aggregated by date
        - monthly_sales_summary: Aggregated by month
        """
        try:
            logger.info("Retrieving Sale Register data")
            
            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))
            register_type = request.query_params.get('register_type', 'general')
            
            # Get cancelled status IDs
            canceled_status_ids = list(OrderStatuses.objects.filter(
                status_name__in=['Cancelled']
            ).values_list('order_status_id', flat=True))
            
            # Base queryset based on register type
            if register_type == 'cancelled':
                # Only cancelled invoices
                queryset = SaleInvoiceOrders.objects.filter(
                    order_status_id__in=canceled_status_ids
                )
            else:
                # Exclude cancelled
                queryset = SaleInvoiceOrders.objects.exclude(
                    order_status_id__in=canceled_status_ids
                ).exclude(is_deleted=True)
            
            queryset = queryset.select_related(
                'customer_id', 
                'customer_address_id', 
                'customer_address_id__city_id',
                'order_status_id'
            ).order_by('-created_at')
            
            # Apply filters
            filterset = SaleRegisterFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
            
            # Route to appropriate handler based on register_type
            if register_type == 'detailed':
                return self._get_detailed_register(request, queryset, page, limit)
            elif register_type == 'daily_sales_summary':
                return self._get_daily_sales_summary(request, queryset, page, limit)
            elif register_type == 'monthly_sales_summary':
                return self._get_monthly_sales_summary(request, queryset, page, limit)
            elif register_type in ['product_group_wise', 'product_category_wise', 'product_brand_wise', 'hsn_wise']:
                return self._get_columnar_register(request, queryset, register_type, page, limit)
            else:
                # Default: general, tax_wise, cancelled, unprinted, etc.
                return self._get_general_register(request, queryset, register_type, page, limit)
            
        except Exception as e:
            logger.error(f"Error in get_sale_register: {str(e)}")
            import traceback
            traceback.print_exc()
            return build_response(0, f"An error occurred: {str(e)}", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def _get_general_register(self, request, queryset, register_type, page, limit):
        """General Register - Invoice level with flat data for <ta-table> compatibility"""
        total_count = queryset.count()
        
        # Pagination
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_queryset = queryset[start_index:end_index]
        
        # Build flat records array
        records = []
        serial_number = start_index + 1
        
        for invoice in paginated_queryset:
            attachment_count = OrderAttachments.objects.filter(
                order_id=str(invoice.sale_invoice_id),
                is_deleted=False
            ).count()
            
            city = self._get_city(invoice)
            
            records.append({
                's_no': serial_number,
                'sale_invoice_id': str(invoice.sale_invoice_id),
                'voucher_type': invoice.bill_type,
                'date': invoice.invoice_date.strftime('%d-%m-%Y') if invoice.invoice_date else None,
                'invoice_date': str(invoice.invoice_date) if invoice.invoice_date else None,
                'invoice_no': invoice.invoice_no,
                'customer_name': invoice.customer_id.name if invoice.customer_id else None,
                'customer_id': str(invoice.customer_id.customer_id) if invoice.customer_id else None,
                'city': city,
                'gross_amount': float(invoice.item_value or 0),
                'discount': float(invoice.dis_amt or 0),
                'tax_amount': float(invoice.tax_amount or 0),
                'round_off': float(invoice.round_off or 0),
                'amount': float(invoice.total_amount or 0),
                'attachment_count': attachment_count,
                'status': invoice.order_status_id.status_name if invoice.order_status_id else None,
                'order_status_id': str(invoice.order_status_id.order_status_id) if invoice.order_status_id else None
            })
            serial_number += 1
        
        # Calculate grand totals from full queryset (not paginated)
        grand_totals = queryset.aggregate(
            gross_total=Sum('item_value'),
            discount_total=Sum('dis_amt'),
            tax_total=Sum('tax_amount'),
            round_off_total=Sum('round_off'),
            amount_total=Sum('total_amount')
        )
        
        # Return flat response matching your codebase format
        return filter_response(
            count=len(records),
            message="Success",
            data=records,
            page=page,
            limit=limit,
            total_count=total_count,
            status_code=status.HTTP_200_OK
        )

    def _get_detailed_register(self, request, queryset, page, limit):
        """Detailed Register - Product level details with flat data for <ta-table> compatibility"""
        # Get all invoice items for the filtered invoices
        invoice_ids = list(queryset.values_list('sale_invoice_id', flat=True))
        
        items = SaleInvoiceItems.objects.filter(
            sale_invoice_id__in=invoice_ids
        ).select_related(
            'sale_invoice_id',
            'sale_invoice_id__customer_id',
            'product_id',
            'unit_options_id'
        ).order_by('sale_invoice_id__invoice_date', 'sale_invoice_id__invoice_no')
        
        total_count = items.count()
        
        # Pagination
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_items = items[start_index:end_index]
        
        records = []
        serial_number = start_index + 1
        for item in paginated_items:
            invoice = item.sale_invoice_id
            net_amount = (item.quantity or 0) * (item.rate or 0)
            
            records.append({
                's_no': serial_number,
                'sale_invoice_id': str(invoice.sale_invoice_id) if invoice else None,
                'sale_invoice_item_id': str(item.sale_invoice_item_id) if item else None,
                'date': invoice.invoice_date.strftime('%d-%m-%Y') if invoice.invoice_date else None,
                'invoice_date': str(invoice.invoice_date) if invoice.invoice_date else None,
                'doc_no': invoice.invoice_no,
                'customer_name': invoice.customer_id.name if invoice.customer_id else None,
                'customer_id': str(invoice.customer_id.customer_id) if invoice.customer_id else None,
                'product_name': item.product_id.name if item.product_id else None,
                'product_id': str(item.product_id.product_id) if item.product_id else None,
                'qty': float(item.quantity or 0),
                'unit_name': item.unit_options_id.unit_name if item.unit_options_id else 'NOS',
                'rate': float(item.rate or 0),
                'net_amount': float(net_amount),
                'amount': float(item.amount or 0)
            })
            serial_number += 1
        
        # Return flat response matching your codebase format
        return filter_response(
            count=len(records),
            message="Success",
            data=records,
            page=page,
            limit=limit,
            total_count=total_count,
            status_code=status.HTTP_200_OK
        )

    def _get_daily_sales_summary(self, request, queryset, page, limit):
        """Daily Sales Summary - Aggregated by date with flat data for <ta-table> compatibility"""
        from django.db.models.functions import TruncDate
        
        daily_data = queryset.annotate(
            sale_date=TruncDate('invoice_date')
        ).values('sale_date').annotate(
            invoice_count=Count('sale_invoice_id'),
            gross_total=Sum('item_value'),
            discount_total=Sum('dis_amt'),
            tax_total=Sum('tax_amount'),
            amount_total=Sum('total_amount')
        ).order_by('sale_date')
        
        total_count = daily_data.count()
        
        # Pagination
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_data = list(daily_data[start_index:end_index])
        
        records = []
        serial_number = start_index + 1
        for row in paginated_data:
            records.append({
                's_no': serial_number,
                'date': row['sale_date'].strftime('%d-%m-%Y') if row['sale_date'] else None,
                'sale_date': str(row['sale_date']) if row['sale_date'] else None,
                'invoice_count': row['invoice_count'],
                'gross_total': float(row['gross_total'] or 0),
                'discount_total': float(row['discount_total'] or 0),
                'tax_total': float(row['tax_total'] or 0),
                'amount_total': float(row['amount_total'] or 0)
            })
            serial_number += 1
        
        # Return flat response matching your codebase format
        return filter_response(
            count=len(records),
            message="Success",
            data=records,
            page=page,
            limit=limit,
            total_count=total_count,
            status_code=status.HTTP_200_OK
        )

    def _get_monthly_sales_summary(self, request, queryset, page, limit):
        """Monthly Sales Summary - Aggregated by month with flat data for <ta-table> compatibility"""
        from django.db.models.functions import TruncMonth
        
        monthly_data = queryset.annotate(
            sale_month=TruncMonth('invoice_date')
        ).values('sale_month').annotate(
            invoice_count=Count('sale_invoice_id'),
            gross_total=Sum('item_value'),
            discount_total=Sum('dis_amt'),
            tax_total=Sum('tax_amount'),
            amount_total=Sum('total_amount')
        ).order_by('sale_month')
        
        total_count = monthly_data.count()
        
        # Pagination
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_data = list(monthly_data[start_index:end_index])
        
        records = []
        serial_number = start_index + 1
        for row in paginated_data:
            records.append({
                's_no': serial_number,
                'month': row['sale_month'].strftime('%B %Y') if row['sale_month'] else None,
                'month_year': row['sale_month'].strftime('%Y-%m') if row['sale_month'] else None,
                'invoice_count': row['invoice_count'],
                'gross_total': float(row['gross_total'] or 0),
                'discount_total': float(row['discount_total'] or 0),
                'tax_total': float(row['tax_total'] or 0),
                'amount_total': float(row['amount_total'] or 0)
            })
            serial_number += 1
        
        # Return flat response matching your codebase format
        return filter_response(
            count=len(records),
            message="Success",
            data=records,
            page=page,
            limit=limit,
            total_count=total_count,
            status_code=status.HTTP_200_OK
        )

    def _get_columnar_register(self, request, queryset, register_type, page, limit):
        """Columnar Register - Grouped by Product Group/Category/Brand/HSN with flat data for <ta-table> compatibility"""
        invoice_ids = list(queryset.values_list('sale_invoice_id', flat=True))
        
        items = SaleInvoiceItems.objects.filter(
            sale_invoice_id__in=invoice_ids
        ).select_related(
            'sale_invoice_id',
            'product_id',
            'product_id__product_group_id',
            'product_id__brand_id',
            'unit_options_id'
        )
        
        # Determine grouping field
        if register_type == 'product_group_wise':
            group_field = 'product_id__product_group_id__group_name'
            group_id_field = 'product_id__product_group_id'
            display_name = 'Product Group'
        elif register_type == 'product_category_wise':
            group_field = 'product_id__category_id__category_name'
            group_id_field = 'product_id__category_id'
            display_name = 'Product Category'
        elif register_type == 'product_brand_wise':
            group_field = 'product_id__brand_id__brand_name'
            group_id_field = 'product_id__brand_id'
            display_name = 'Product Brand'
        elif register_type == 'hsn_wise':
            group_field = 'product_id__hsn_code'
            group_id_field = 'product_id__hsn_code'
            display_name = 'HSN Code'
        else:
            group_field = 'product_id__product_group_id__group_name'
            group_id_field = 'product_id__product_group_id'
            display_name = 'Product Group'
        
        # Aggregate by group
        grouped_data = items.values(group_field).annotate(
            qty_total=Sum('quantity'),
            amount_total=Sum('amount'),
            item_count=Count('sale_invoice_item_id')
        ).order_by(group_field)
        
        total_count = grouped_data.count()
        
        # Pagination
        start_index = (page - 1) * limit
        end_index = start_index + limit
        paginated_data = list(grouped_data[start_index:end_index])
        
        records = []
        serial_number = start_index + 1
        for row in paginated_data:
            records.append({
                's_no': serial_number,
                'group_name': row[group_field] or 'Uncategorized',
                'group_type': display_name,
                'item_count': row['item_count'],
                'qty_total': float(row['qty_total'] or 0),
                'amount_total': float(row['amount_total'] or 0)
            })
            serial_number += 1
        
        # Return flat response matching your codebase format
        return filter_response(
            count=len(records),
            message="Success",
            data=records,
            page=page,
            limit=limit,
            total_count=total_count,
            status_code=status.HTTP_200_OK
        )

    def _get_city(self, invoice):
        """Helper to get city from invoice"""
        try:
            if invoice.customer_address_id and invoice.customer_address_id.city_id:
                return invoice.customer_address_id.city_id.city_name
            elif invoice.customer_id:
                from apps.customer.models import CustomerAddresses
                address = CustomerAddresses.objects.filter(
                    customer_id=invoice.customer_id
                ).first()
                if address and address.city_id:
                    return address.city_id.city_name
        except Exception:
            pass
        return None
    
    # def retrieve(self, request, *args, **kwargs):
    #     """
    #     Retrieves a sale invoice order and its related data (items, attachments, and shipments).
    #     """
    #     try:
    #         pk = kwargs.get('pk')
    #         if not pk:
    #             logger.error("Primary key not provided in request.")
    #             return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

    #         # Step 1: Try to fetch from mstcnl
    #         try:
    #             sale_invoice_order = MstcnlSaleInvoiceOrder.objects.using('mstcnl').get(pk=pk)
    #             using_db = 'mstcnl'
    #             logger.info(f"SaleInvoiceOrders found in 'mstcnl' database with pk: {pk}")

    #             # Use mstcnl models
    #             ItemsModel = MstcnlSaleInvoiceItem
    #             AttachmentsModel = MstcnlOrderAttachment
    #             ShipmentsModel = MstcnlOrderShipment
    #             CustomFieldsModel = MstcnlCustomFieldValue
    #             OrderSerializer = MstcnlSaleInvoiceSerializer

    #         except MstcnlSaleInvoiceOrder.DoesNotExist:
    #             # Step 2: If not found in mstcnl, try devcnl (default)
    #             try:
    #                 sale_invoice_order = SaleInvoiceOrders.objects.using('default').get(pk=pk)
    #                 using_db = 'default'
    #                 logger.info(f"SaleInvoiceOrders found in 'devcnl' database with pk: {pk}")

    #                 # Use default models
    #                 ItemsModel = SaleInvoiceItems
    #                 AttachmentsModel = OrderAttachments
    #                 ShipmentsModel = OrderShipments
    #                 CustomFieldsModel = CustomFieldValue
    #                 OrderSerializer = SaleInvoiceOrdersSerializer

    #             except SaleInvoiceOrders.DoesNotExist:
    #                 # Step 3: Not found anywhere
    #                 logger.error(f"SaleInvoiceOrders with pk {pk} does not exist in any database.")
    #                 return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    #         # Retrieve the SaleInvoiceOrders instance
    #         # sale_invoice_order_serializer = SaleInvoiceOrdersSerializer(sale_invoice_order)
    #         sale_invoice_order_serializer = OrderSerializer(sale_invoice_order)

    #         # Retrieve related data
    #         items_data = self.get_related_data(ItemsModel, SaleInvoiceItemsSerializer, 'sale_invoice_id', pk, using_db)
    #         attachments_data = self.get_related_data(AttachmentsModel, OrderAttachmentsSerializer, 'order_id', pk, using_db)
    #         shipments_data = self.get_related_data(ShipmentsModel, OrderShipmentsSerializer, 'order_id', pk, using_db)
    #         shipments_data = shipments_data[0] if len(shipments_data) > 0 else {}

    #         # Retrieve custom field values
    #         custom_field_values_data = self.get_related_data(CustomFieldsModel, CustomFieldValueSerializer, 'custom_id', pk, using_db)

    #         # Customizing the response data
    #         custom_data = {
    #             "sale_invoice_order": sale_invoice_order_serializer.data,
    #             "sale_invoice_items": items_data,
    #             "order_attachments": attachments_data,
    #             "order_shipments": shipments_data,
    #             "custom_field_values": custom_field_values_data
    #         }
    #         logger.info("Sale invoice order and related data retrieved successfully.")
    #         return build_response(1, "Success", custom_data, status.HTTP_200_OK)

    #     except Http404:
    #         logger.error("Sale invoice order with pk %s does not exist.", pk)
    #         return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         logger.exception(
    #             "An error occurred while retrieving sale invoice order with pk %s: %s", pk, str(e))
    #         return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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
                sale_invoice_order = MstcnlSaleInvoiceOrder.objects.using('mstcnl').get(pk=pk)
                using_db = 'mstcnl'
                logger.info(f"SaleInvoiceOrders found in 'mstcnl' database with pk: {pk}")

                # mstcnl models + serializers
                ItemsModel, ItemsSerializer = MstcnlSaleInvoiceItem, MstcnlSaleInvoiceItemSerializer
                AttachmentsModel, AttachmentsSerializer = MstcnlOrderAttachment, MstcnlOrderAttachmentsSerializer
                ShipmentsModel, ShipmentsSerializer = MstcnlOrderShipment, MstcnlOrderShipmentsSerializer
                CustomFieldsModel, CustomFieldsSerializer = MstcnlCustomFieldValue, MstcnlCustomFieldValueSerializer
                OrderSerializer = MstcnlSaleInvoiceSerializer

            except MstcnlSaleInvoiceOrder.DoesNotExist:
                # Step 2: If not found in mstcnl, try default
                try:
                    sale_invoice_order = SaleInvoiceOrders.objects.using('default').get(pk=pk)
                    using_db = 'default'
                    logger.info(f"SaleInvoiceOrders found in 'default' database with pk: {pk}")

                    # default models + serializers
                    ItemsModel, ItemsSerializer = SaleInvoiceItems, SaleInvoiceItemsSerializer
                    AttachmentsModel, AttachmentsSerializer = OrderAttachments, OrderAttachmentsSerializer
                    ShipmentsModel, ShipmentsSerializer = OrderShipments, OrderShipmentsSerializer
                    CustomFieldsModel, CustomFieldsSerializer = CustomFieldValue, CustomFieldValueSerializer
                    OrderSerializer = SaleInvoiceOrdersSerializer

                except SaleInvoiceOrders.DoesNotExist:
                    logger.error(f"SaleInvoiceOrders with pk {pk} does not exist in any database.")
                    return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

            # --- Serialization ---
            sale_invoice_order_serializer = OrderSerializer(sale_invoice_order)

            items_data = self.get_related_data(ItemsModel, ItemsSerializer, 'sale_invoice_id', pk, using_db)
            attachments_data = self.get_related_data(AttachmentsModel, AttachmentsSerializer, 'order_id', pk, using_db)
            shipments_data = self.get_related_data(ShipmentsModel, ShipmentsSerializer, 'order_id', pk, using_db)
            shipments_data = shipments_data[0] if len(shipments_data) > 0 else {}
            custom_field_values_data = self.get_related_data(CustomFieldsModel, CustomFieldsSerializer, 'custom_id', pk, using_db)

            # Final response
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
        
    # @transaction.atomic
    # def delete(self, request, pk, *args, **kwargs):
    #     """
    #     Handles the cancellation of a sale invoice order:
    #     - Marks it as 'Cancelled' instead of deleting
    #     - Reverts products back to inventory
    #     - Creates reversing ledger entry
    #     """
    #     db_to_use = None
    #     try:
    #         # Determine which database to use
    #         try:
    #             SaleInvoiceOrders.objects.using('mstcnl').get(sale_invoice_id=pk)
    #             set_db('mstcnl')
    #             db_to_use = 'mstcnl'
    #         except SaleInvoiceOrders.DoesNotExist:
    #             SaleInvoiceOrders.objects.using('default').get(sale_invoice_id=pk)
    #             set_db('default')
    #             db_to_use = 'default'
    #     except SaleInvoiceOrders.DoesNotExist:
    #         logger.warning(f"Sale Invoice Orders with ID {pk} does not exist in any database.")
    #         return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    #     try:
    #         # Get the SaleInvoiceOrders instance
    #         instance = SaleInvoiceOrders.objects.using(db_to_use).get(pk=pk)

    #         # Get the "Cancelled" status
    #         try:
    #             canceled_status = OrderStatuses.objects.using(db_to_use).get(status_name='Cancelled')
    #         except OrderStatuses.DoesNotExist:
    #             logger.error("'Cancelled' status not found in OrderStatuses table")
    #             return build_response(0, "Cannot cancel invoice - required status not found", [], status.HTTP_400_BAD_REQUEST)

    #         # --- STEP 1: Update invoice status to "Cancelled"
    #         instance.order_status_id = canceled_status
    #         instance.save(using=db_to_use)
    #         invoice_no = instance.invoice_no
    #         customer_id = instance.customer_id

    #         # --- STEP 2: Revert products back to inventory
    #         try:
    #             invoice_items = SaleInvoiceItems.objects.using(db_to_use).filter(sale_invoice_id=instance.sale_invoice_id)

    #             for item in invoice_items:
    #                 product = item.product_id  # ForeignKey to Product
    #                 # Safely increase the available quantity
    #                 product.balance = F('balance') + item.quantity
    #                 product.save(using=db_to_use)

    #             logger.info(f"Reverted {len(invoice_items)} products to inventory for cancelled invoice {invoice_no}")

    #         except Exception as e:
    #             logger.error(f"Error reverting products to inventory for invoice {invoice_no}: {str(e)}")

    #         # --- STEP 3: Create offsetting ledger entry
    #         existing_balance = (
    #             JournalEntryLines.objects.filter(customer_id=customer_id)
    #             .order_by('is_deleted', '-created_at')
    #             .values_list('balance', flat=True)
    #             .first()
    #         ) or Decimal('0.00')

    #         latest_balance = existing_balance - Decimal(instance.total_amount)

    #         try:
    #             journal_entry = JournalEntryLines.objects.using(db_to_use).create(
    #                 description=f"Cancellation of invoice {invoice_no}",
    #                 credit=instance.total_amount,
    #                 debit=0,
    #                 voucher_no=invoice_no,
    #                 customer_id=customer_id,
    #                 balance=latest_balance
    #             )
    #             logger.info(f"Created offsetting credit entry of {instance.total_amount} for cancelled invoice {invoice_no}")
    #         except Exception as e:
    #             logger.error(f"Error creating offsetting credit entry: {str(e)}")

    #         # --- STEP 4: Return success response
    #         return build_response(1, "Invoice cancelled successfully", [], status.HTTP_200_OK)

    #     except SaleInvoiceOrders.DoesNotExist:
    #         logger.warning(f"SaleInvoiceOrders with ID {pk} does not exist.")
    #         return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         logger.error(f"Error cancelling SaleInvoiceOrders with ID {pk}: {str(e)}")
    #         return build_response(0, "Invoice cancellation failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the cancellation or permanent deletion of a sale invoice order:
        - If bill_type='Others' & order_status='Completed' → permanently delete and replicate
        - Otherwise → mark as 'Cancelled', revert stock, and create ledger reversal
        """
        db_to_use = None
        try:
            # Determine which database to use
            try:
                SaleInvoiceOrders.objects.using('mstcnl').get(sale_invoice_id=pk)
                set_db('mstcnl')
                db_to_use = 'mstcnl'
            except SaleInvoiceOrders.DoesNotExist:
                SaleInvoiceOrders.objects.using('default').get(sale_invoice_id=pk)
                set_db('default')
                db_to_use = 'default'
        except SaleInvoiceOrders.DoesNotExist:
            logger.warning(f"Sale Invoice Orders with ID {pk} does not exist in any database.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

        try:
            instance = SaleInvoiceOrders.objects.using(db_to_use).get(pk=pk)

            # ✅ STEP 0: Check if this invoice qualifies for PERMANENT DELETION
            if instance.bill_type == "Others" and instance.order_status_id.status_name == "Completed":
                logger.info(f"Deleting permanently: Invoice {instance.invoice_no} (bill_type='Others', status='Completed')")

                # First replicate record to mstcnl if needed
                try:
                    result = replicate_sale_invoice_to_mstcnl(instance.sale_invoice_id)
                    logger.info(f"Replication result for invoice {instance.invoice_no}: {result}")
                except Exception as e:
                    logger.error(f"Error replicating invoice {instance.invoice_no} to mstcnl: {str(e)}")

                # Now permanently delete from the current database
                instance.delete(using=db_to_use)
                logger.info(f"Invoice {instance.invoice_no} permanently deleted from {db_to_use} database.")

                return build_response(1, "Invoice permanently deleted successfully", [], status.HTTP_204_NO_CONTENT)

            # ---------------------------------------------
            # Default Cancellation Flow (Existing Logic)
            # ---------------------------------------------
            try:
                canceled_status = OrderStatuses.objects.using(db_to_use).get(status_name='Cancelled')
            except OrderStatuses.DoesNotExist:
                logger.error("'Cancelled' status not found in OrderStatuses table")
                return build_response(0, "Cannot cancel invoice - required status not found", [], status.HTTP_400_BAD_REQUEST)

            instance.order_status_id = canceled_status
            instance.save(using=db_to_use)
            invoice_no = instance.invoice_no
            customer_id = instance.customer_id

            # --- STEP 2: Revert products back to inventory
            try:
                invoice_items = SaleInvoiceItems.objects.using(db_to_use).filter(sale_invoice_id=instance.sale_invoice_id)
                for item in invoice_items:
                    product = item.product_id
                    product.balance = F('balance') + item.quantity
                    product.save(using=db_to_use)
                logger.info(f"Reverted {len(invoice_items)} products to inventory for cancelled invoice {invoice_no}")
            except Exception as e:
                logger.error(f"Error reverting products to inventory for invoice {invoice_no}: {str(e)}")

            # --- STEP 3: Create offsetting ledger entry
            existing_balance = (
                JournalEntryLines.objects.filter(customer_id=customer_id)
                .order_by('is_deleted', '-created_at')
                .values_list('balance', flat=True)
                .first()
            ) or Decimal('0.00')

            latest_balance = existing_balance - Decimal(instance.total_amount)
            try:
                JournalEntryLines.objects.using(db_to_use).create(
                    description=f"Cancellation of invoice {invoice_no}",
                    credit=instance.total_amount,
                    debit=0,
                    voucher_no=invoice_no,
                    customer_id=customer_id,
                    balance=latest_balance
                )
                logger.info(f"Created offsetting credit entry of {instance.total_amount} for cancelled invoice {invoice_no}")
            except Exception as e:
                logger.error(f"Error creating offsetting credit entry: {str(e)}")

            return build_response(1, "Invoice cancelled successfully", [], status.HTTP_200_OK)

        except SaleInvoiceOrders.DoesNotExist:
            logger.warning(f"SaleInvoiceOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error cancelling SaleInvoiceOrders with ID {pk}: {str(e)}")
            return build_response(0, "Invoice cancellation failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    # @transaction.atomic
    # def delete(self, request, pk, *args, **kwargs):
    #     """
    #     Handles the deletion of a sale invoice order and its related attachments and shipments.
    #     """
    #     db_to_use = None
    #     try:
    #         # Check which database the SaleInvoiceOrders belongs to
    #         SaleInvoiceOrders.objects.using('mstcnl').get(sale_invoice_id=pk)
    #         set_db('mstcnl')
    #         db_to_use = 'mstcnl'
    #     except SaleInvoiceOrders.DoesNotExist:
    #         try:
    #             SaleInvoiceOrders.objects.using('default').get(sale_invoice_id=pk)
    #             set_db('default')
    #             db_to_use = 'default'
    #         except SaleInvoiceOrders.DoesNotExist:
    #             logger.warning(f"Sale Invoice Orders with ID {pk} does not exist in any database.")
    #             return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
    #     try:
    #         # Get the SaleInvoiceOrders instance
    #         instance = SaleInvoiceOrders.objects.using(db_to_use).get(pk=pk)
            
    #          # Get or create "Canceled" order status
    #         canceled_status = None
    #         try:
    #             canceled_status = OrderStatuses.objects.using(db_to_use).get(status_name='Cancelled')
    #         except OrderStatuses.DoesNotExist:
    #             logger.error("'Cancelled' status found in OrderStatuses table")
    #             return build_response(0, "Cannot cancel invoice - required status not found", [], status.HTTP_400_BAD_REQUEST)
            
    #         # Store the invoice amount before marking as canceled
    #         # invoice_amount = instance.total_amount
    #         customer_id = instance.customer_id
    #         invoice_no = instance.invoice_no
            
    #         # Update the invoice status to "Cancelled" instead of deleting
    #         instance.order_status_id = canceled_status
    #         instance.save(using=db_to_use)
    #         existing_balance = (JournalEntryLines.objects.filter(customer_id=instance.customer_id)
    #                                                                         .order_by('is_deleted', '-created_at')                   # most recent entry first
    #                                                                         .values_list('balance', flat=True)         # get only the balance field
    #                                                                         .first()) or Decimal('0.00')               # grab the first result
    #         # new_balance =  Decimal(instance.total_amount) - Decimal(existing_balance)
    #         latest_balance = existing_balance - Decimal(instance.total_amount)

            
    #         # Create offsetting credit entry in the finance system
    #         try:
    #             # Here we would typically call your finance module to create a credit entry
    #             # This is a placeholder - implement according to your actual finance module
    #             journal_entry = JournalEntryLines.objects.using(db_to_use).create(
    #                 description=f"Cancellation of invoice {invoice_no}",
    #                 credit=instance.total_amount,
    #                 debit=0,
    #                 voucher_no=invoice_no,
    #                 customer_id=customer_id,
    #                 balance=latest_balance  
    #             )
    #             logger.info(f"Created offsetting credit entry of {instance.total_amount} for canceled invoice {invoice_no}")

                
    #         except Exception as e:
    #             logger.error(f"Error creating offsetting credit entry: {str(e)}")
            
    #         # Return success response for cancellation
    #         return build_response(1, "Invoice cancelled successfully", [], status.HTTP_200_OK)
            
    #         # # Delete related OrderAttachments and OrderShipments
    #         # if not delete_multi_instance(pk, SaleInvoiceOrders, OrderAttachments, main_model_field_name='order_id'):
    #         #     return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         # if not delete_multi_instance(pk, SaleInvoiceOrders, OrderShipments, main_model_field_name='order_id'):
    #         #     return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         # if not delete_multi_instance(pk, SaleInvoiceOrders, CustomFieldValue, main_model_field_name='custom_id'):
    #         #     return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    #         # # Delete the main SaleInvoiceOrder instance from the correct database
    #         # instance.delete(using=db_to_use)

    #         # logger.info(f"SaleInvoiceOrders with ID {pk} deleted successfully.")
    #         # return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
    #     except SaleInvoiceOrders.DoesNotExist:
    #         logger.warning(f"SaleInvoiceOrders with ID {pk} does not exist.")
    #         return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         logger.error(f"Error deleting SaleInvoiceOrders with ID {pk}: {str(e)}")
    #         return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    # @transaction.atomic
    # def create(self, request, *args, **kwargs):
    #     given_data = request.data

    #     # Determine DB before any validation
    #     # bill_type = given_data.get('sale_invoice_order', {}).get('bill_type')

    #     # is_other_bill = bill_type == "OTHERS"

    #     using_db = 'default'
    #     set_db(using_db)

    #     # Extract payload
    #     sale_invoice_data = given_data.pop('sale_invoice_order', None)
    #     sale_invoice_items_data = given_data.pop('sale_invoice_items', None)
    #     order_attachments_data = given_data.pop('order_attachments', None)
    #     order_shipments_data = given_data.pop('order_shipments', None)
    #     custom_fields_data = given_data.pop('custom_field_values', None)
        
    #     # ---------------- CLEAN EMPTY SALE ORDER ITEMS ---------------- #
    #     # Remove blank/empty payloads created by frontend (5 default rows)
    #     # 👉 ADD THIS BELOW
    #     sale_invoice_items_data = [
    #         item for item in sale_invoice_items_data
    #         if item.get("product_id") and item.get("quantity")
    #     ]
    #     #----------------------------------------------------------

    #     # ---------------------- VALIDATION ----------------------------------#
    #     invoice_error, item_error, attachment_error, shipment_error, custom_error = [], [], [], [], []

    #     if sale_invoice_data:
    #         invoice_error = validate_payload_data(self, sale_invoice_data, SaleInvoiceOrdersSerializer, using=using_db)
    #         validate_order_type(sale_invoice_data, invoice_error, OrderTypes, look_up='order_type')
            
    #     if sale_invoice_items_data:
    #         item_error = validate_multiple_data(self, sale_invoice_items_data, SaleInvoiceItemsSerializer, ['sale_invoice_id'], using_db=using_db)

    #     if order_attachments_data:
    #         attachment_error = validate_multiple_data(self, order_attachments_data, OrderAttachmentsSerializer, ['order_id', 'order_type_id'], using_db=using_db)

    #     if order_shipments_data:
    #         if len(order_shipments_data) > 1:
    #             shipment_error = validate_multiple_data(self, [order_shipments_data], OrderShipmentsSerializer, ['order_id', 'order_type_id'], using_db=using_db)
    #         else:
    #             order_shipments_data = {}
    #             shipment_error = []

    #     if custom_fields_data:
    #         custom_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'], using_db=using_db)

    #     if not sale_invoice_data or not sale_invoice_items_data:
    #         logger.error("Sale invoice and items & CustomFields are mandatory but not provided.")
    #         return build_response(0, "Sale invoice and items & CustomFields are mandatory", [], status.HTTP_400_BAD_REQUEST)

    #     errors = {}
    #     if invoice_error: errors["sale_invoice_order"] = invoice_error
    #     if item_error: errors["sale_invoice_items"] = item_error
    #     if attachment_error: errors["order_attachments"] = attachment_error
    #     if shipment_error: errors["order_shipments"] = shipment_error
    #     if custom_error: errors["custom_field_values"] = custom_error

    #     if errors:
    #         return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

    #     # ---------------------- D A T A   C R E A T I O N ----------------------------#
    #     new_invoice_data = generic_data_creation(self, [sale_invoice_data], SaleInvoiceOrdersSerializer, using=using_db)[0]
    #     sale_invoice_id = new_invoice_data.get("sale_invoice_id", None)
    #     logger.info(f'SaleInvoiceOrder - created in {using_db} DB')

    #     # Update child data with invoice_id
    #     if sale_invoice_id:
    #         update_fields = {'sale_invoice_id': sale_invoice_id}
    #         invoice_items = generic_data_creation(self, sale_invoice_items_data, SaleInvoiceItemsSerializer, update_fields, using=using_db)
    #         logger.info(f'SaleInvoiceItems - created in {using_db} DB')

    #     order_type_val = sale_invoice_data.get('order_type')
    #     order_type = get_object_or_none(OrderTypes, name=order_type_val)
    #     type_id = order_type.order_type_id if order_type else None

    #     update_fields = {'order_id': sale_invoice_id, 'order_type_id': type_id}
    #     if order_attachments_data:
    #         order_attachments = generic_data_creation(self, order_attachments_data, OrderAttachmentsSerializer, update_fields, using=using_db)
    #         logger.info(f'OrderAttachments - created in {using_db} DB')
    #     else:
    #         order_attachments = []

    #     if order_shipments_data:
    #         order_shipments = generic_data_creation(self, [order_shipments_data], OrderShipmentsSerializer, update_fields, using=using_db)
    #         logger.info(f'OrderShipments - created in {using_db} DB')
    #     else:
    #         order_shipments = []

    #     if custom_fields_data:
    #         update_fields = {'custom_id': sale_invoice_id}
    #         custom_fields = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, update_fields, using=using_db)
    #         logger.info(f'CustomFieldValues - created in {using_db} DB')
    #     else:
    #         custom_fields = []

    #     # ---------------------- R E S P O N S E ----------------------------#
    #     custom_data = {
    #         "sale_invoice_order": new_invoice_data,
    #         "sale_invoice_items": invoice_items,
    #         "order_attachments": order_attachments,
    #         "order_shipments": order_shipments,
    #         "custom_field_values": custom_fields
    #     }
        
    #     saleinvocie_no = sale_invoice_data.get("invoice_no")
    #     # Log the Create
    #     log_user_action(
    #         using_db,
    #         request.user,
    #         "CREATE",
    #         "Sale Invoice",
    #         sale_invoice_id,
    #         f"{saleinvocie_no} - Sale Invoice Record Created by {request.user.username}"
    #     )
    #     return build_response(1, "Sale Invoice created successfully", custom_data, status.HTTP_201_CREATED)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        given_data = request.data

        using_db = 'default'
        set_db(using_db)

        # Extract payload
        sale_invoice_data = given_data.pop('sale_invoice_order', None)
        sale_invoice_items_data = given_data.pop('sale_invoice_items', None)
        order_attachments_data = given_data.pop('order_attachments', None)
        order_shipments_data = given_data.pop('order_shipments', None)
        custom_fields_data = given_data.pop('custom_field_values', None)
        
        # ---------------- CLEAN EMPTY SALE ORDER ITEMS ---------------- #
        sale_invoice_items_data = [
            item for item in sale_invoice_items_data
            if item.get("product_id") and item.get("quantity")
        ]
        #----------------------------------------------------------

        # ---------------------- VALIDATION ----------------------------------#
        invoice_error, item_error, attachment_error, shipment_error, custom_error = [], [], [], [], []

        if sale_invoice_data:
            invoice_error = validate_payload_data(
                self, sale_invoice_data, SaleInvoiceOrdersSerializer, using=using_db
            )
            validate_order_type(sale_invoice_data, invoice_error, OrderTypes, look_up='order_type')
            
        if sale_invoice_items_data:
            item_error = validate_multiple_data(
                self, sale_invoice_items_data, SaleInvoiceItemsSerializer,
                ['sale_invoice_id'], using_db=using_db
            )

        if order_attachments_data:
            attachment_error = validate_multiple_data(
                self, order_attachments_data, OrderAttachmentsSerializer,
                ['order_id', 'order_type_id'], using_db=using_db
            )

        if order_shipments_data:
            if len(order_shipments_data) > 1:
                shipment_error = validate_multiple_data(
                    self, [order_shipments_data], OrderShipmentsSerializer,
                    ['order_id', 'order_type_id'], using_db=using_db
                )
            else:
                order_shipments_data = {}
                shipment_error = []

        if custom_fields_data:
            custom_error = validate_multiple_data(
                self, custom_fields_data, CustomFieldValueSerializer,
                ['custom_id'], using_db=using_db
            )

        if not sale_invoice_data or not sale_invoice_items_data:
            logger.error("Sale invoice and items & CustomFields are mandatory but not provided.")
            return build_response(
                0,
                "Sale invoice and items & CustomFields are mandatory",
                [],
                status.HTTP_400_BAD_REQUEST
            )

        errors = {}
        if invoice_error: errors["sale_invoice_order"] = invoice_error
        if item_error: errors["sale_invoice_items"] = item_error
        if attachment_error: errors["order_attachments"] = attachment_error
        if shipment_error: errors["order_shipments"] = shipment_error
        if custom_error: errors["custom_field_values"] = custom_error

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        new_invoice_data = generic_data_creation(
            self, [sale_invoice_data], SaleInvoiceOrdersSerializer, using=using_db
        )[0]

        sale_invoice_id = new_invoice_data.get("sale_invoice_id", None)
        logger.info(f'SaleInvoiceOrder - created in {using_db} DB')

        # Update child data with invoice_id
        if sale_invoice_id:
            update_fields = {'sale_invoice_id': sale_invoice_id}
            invoice_items = generic_data_creation(
                self,
                sale_invoice_items_data,
                SaleInvoiceItemsSerializer,
                update_fields,
                using=using_db
            )
            logger.info(f'SaleInvoiceItems - created in {using_db} DB')
        
        # # ===================== UPDATE PENDING (production_qty) ===================== #
        # from django.db.models import F

        # for item in sale_invoice_items_data:
        #     sale_order_item_id = item.get("sale_order_item_id")
        #     invoiced_qty = int(item.get("quantity", 0))

        #     if sale_order_item_id and invoiced_qty > 0:
        #         SaleOrderItems.objects.using(using_db).filter(
        #             sale_order_item_id=sale_order_item_id
        #         ).update(
        #             production_qty=F('production_qty') - invoiced_qty
        #         )
        # # ========================================================================== #


        order_type_val = sale_invoice_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id if order_type else None

        update_fields = {'order_id': sale_invoice_id, 'order_type_id': type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(
                self, order_attachments_data, OrderAttachmentsSerializer,
                update_fields, using=using_db
            )
            logger.info(f'OrderAttachments - created in {using_db} DB')
        else:
            order_attachments = []

        if order_shipments_data:
            order_shipments = generic_data_creation(
                self, [order_shipments_data], OrderShipmentsSerializer,
                update_fields, using=using_db
            )
            logger.info(f'OrderShipments - created in {using_db} DB')
        else:
            order_shipments = []

        if custom_fields_data:
            update_fields = {'custom_id': sale_invoice_id}
            custom_fields = generic_data_creation(
                self, custom_fields_data, CustomFieldValueSerializer,
                update_fields, using=using_db
            )
            logger.info(f'CustomFieldValues - created in {using_db} DB')
        else:
            custom_fields = []

        # ---------------------- J O U R N A L   E N T R Y ----------------------------#
        from decimal import Decimal

        invoice_obj = SaleInvoiceOrders.objects.get(
            sale_invoice_id=sale_invoice_id
        )

        # Set pending amount
        invoice_obj.pending_amount = invoice_obj.total_amount
        invoice_obj.save(update_fields=['pending_amount'])

        # Previous balance
        existing_balance = (
            JournalEntryLines.objects
            .filter(customer_id=invoice_obj.customer_id)
            .order_by('is_deleted', '-created_at')
            .values_list('balance', flat=True)
            .first()
        ) or Decimal('0.00')

        new_balance = Decimal(existing_balance) + Decimal(invoice_obj.total_amount)

        sale_account = LedgerAccounts.objects.get(name__iexact="Sale Account")

        # Product description
        invoice_items_qs = SaleInvoiceItems.objects.filter(
            sale_invoice_id=sale_invoice_id
        )

        # product_lines = []
        product_lines = []
        for idx, item in enumerate(invoice_items_qs, start=1):
            product_lines.append(
                f"{idx}) {item.product_id.name} – Qty: {item.quantity:.2f} @ {item.rate:.2f}"
            )

        products_description = "\n".join(product_lines)

        # products_description = "\n".join(product_lines)

        description = (
            f"Goods sold to {invoice_obj.customer_id.name}\n"
            f"{products_description}"
        )

        JournalEntryLines.objects.create(
            ledger_account_id=sale_account,
            debit=invoice_obj.total_amount,
            credit=Decimal('0.00'),
            voucher_no=invoice_obj.invoice_no,
            description=description,
            customer_id=invoice_obj.customer_id,
            balance=new_balance
        )

        # ---------------------- R E S P O N S E ----------------------------#
        custom_data = {
            "sale_invoice_order": new_invoice_data,
            "sale_invoice_items": invoice_items,
            "order_attachments": order_attachments,
            "order_shipments": order_shipments,
            "custom_field_values": custom_fields
        }
        
        saleinvocie_no = sale_invoice_data.get("invoice_no")

        log_user_action(
            using_db,
            request.user,
            "CREATE",
            "Sale Invoice",
            sale_invoice_id,
            f"{saleinvocie_no} - Sale Invoice Record Created by {request.user.username}"
        )

        return build_response(
            1,
            "Sale Invoice created successfully",
            custom_data,
            status.HTTP_201_CREATED
        )
    # @transaction.atomic
    # def create(self, request, *args, **kwargs):
    #     given_data = request.data

    #     using_db = 'default'
    #     set_db(using_db)

    #     # ---------------- EXTRACT PAYLOAD ---------------- #
    #     sale_invoice_data = given_data.pop('sale_invoice_order', None)
    #     sale_invoice_items_data = given_data.pop('sale_invoice_items', None)
    #     order_attachments_data = given_data.pop('order_attachments', None)
    #     order_shipments_data = given_data.pop('order_shipments', None)
    #     custom_fields_data = given_data.pop('custom_field_values', None)

    #     # ---------------- CLEAN EMPTY ITEMS ---------------- #
    #     sale_invoice_items_data = [
    #         item for item in sale_invoice_items_data
    #         if item.get("product_id") and item.get("quantity")
    #     ]

    #     # ---------------- VALIDATION ---------------- #
    #     invoice_error, item_error, attachment_error, shipment_error, custom_error = [], [], [], [], []

    #     if sale_invoice_data:
    #         invoice_error = validate_payload_data(
    #             self, sale_invoice_data, SaleInvoiceOrdersSerializer, using=using_db
    #         )
    #         validate_order_type(sale_invoice_data, invoice_error, OrderTypes, look_up='order_type')

    #     if sale_invoice_items_data:
    #         item_error = validate_multiple_data(
    #             self, sale_invoice_items_data,
    #             SaleInvoiceItemsSerializer,
    #             ['sale_invoice_id'], using_db=using_db
    #         )

    #     if order_attachments_data:
    #         attachment_error = validate_multiple_data(
    #             self, order_attachments_data,
    #             OrderAttachmentsSerializer,
    #             ['order_id', 'order_type_id'], using_db=using_db
    #         )

    #     if order_shipments_data:
    #         if len(order_shipments_data) > 1:
    #             shipment_error = validate_multiple_data(
    #                 self, [order_shipments_data],
    #                 OrderShipmentsSerializer,
    #                 ['order_id', 'order_type_id'], using_db=using_db
    #             )
    #         else:
    #             order_shipments_data = {}
    #             shipment_error = []

    #     if custom_fields_data:
    #         custom_error = validate_multiple_data(
    #             self, custom_fields_data,
    #             CustomFieldValueSerializer,
    #             ['custom_id'], using_db=using_db
    #         )

    #     if not sale_invoice_data or not sale_invoice_items_data:
    #         return build_response(
    #             0,
    #             "Sale invoice and items are mandatory",
    #             [],
    #             status.HTTP_400_BAD_REQUEST
    #         )

    #     errors = {}
    #     if invoice_error: errors["sale_invoice_order"] = invoice_error
    #     if item_error: errors["sale_invoice_items"] = item_error
    #     if attachment_error: errors["order_attachments"] = attachment_error
    #     if shipment_error: errors["order_shipments"] = shipment_error
    #     if custom_error: errors["custom_field_values"] = custom_error

    #     if errors:
    #         return build_response(0, "ValidationError", errors, status.HTTP_400_BAD_REQUEST)

    #     # ---------------- CREATE INVOICE ---------------- #
    #     new_invoice_data = generic_data_creation(
    #         self, [sale_invoice_data],
    #         SaleInvoiceOrdersSerializer,
    #         using=using_db
    #     )[0]

    #     sale_invoice_id = new_invoice_data.get("sale_invoice_id")

    #     # ---------------- CREATE ITEMS ---------------- #
    #     if sale_invoice_id:
    #         update_fields = {'sale_invoice_id': sale_invoice_id}
    #         invoice_items = generic_data_creation(
    #             self,
    #             sale_invoice_items_data,
    #             SaleInvoiceItemsSerializer,
    #             update_fields,
    #             using=using_db
    #         )

    #     # ================================================================
    #     # 🔥 INVENTORY + PENDING UPDATE LOGIC (FINAL & SAFE)
    #     # ================================================================
    #     from django.db.models import F

    #     for item in sale_invoice_items_data:
    #         sale_order_item_id = item.get("sale_order_item_id")
    #         product_id = item.get("product_id")
    #         invoiced_qty = int(item.get("quantity", 0))

    #         if invoiced_qty <= 0:
    #             continue

    #         # -------- CASE 1: INVOICE FROM SALE ORDER --------
    #         if sale_order_item_id:
    #             SaleOrderItems.objects.using(using_db).filter(
    #                 sale_order_item_id=sale_order_item_id
    #             ).update(
    #                 production_qty=F('production_qty') - invoiced_qty
    #             )

    #         # -------- CASE 2: DIRECT INVOICE (NO SALE ORDER) --------
    #         else:
    #             Products.objects.using(using_db).filter(
    #                 product_id=product_id
    #             ).update(
    #                 balance=F('balance') - invoiced_qty
    #             )

    #     # ================================================================

    #     # ---------------- ATTACHMENTS / SHIPMENTS ---------------- #
    #     order_type_val = sale_invoice_data.get('order_type')
    #     order_type = get_object_or_none(OrderTypes, name=order_type_val)
    #     type_id = order_type.order_type_id if order_type else None

    #     update_fields = {'order_id': sale_invoice_id, 'order_type_id': type_id}

    #     order_attachments = generic_data_creation(
    #         self, order_attachments_data, OrderAttachmentsSerializer,
    #         update_fields, using=using_db
    #     ) if order_attachments_data else []

    #     order_shipments = generic_data_creation(
    #         self, [order_shipments_data], OrderShipmentsSerializer,
    #         update_fields, using=using_db
    #     ) if order_shipments_data else []

    #     if custom_fields_data:
    #         update_fields = {'custom_id': sale_invoice_id}
    #         custom_fields = generic_data_creation(
    #             self, custom_fields_data,
    #             CustomFieldValueSerializer,
    #             update_fields, using=using_db
    #         )
    #     else:
    #         custom_fields = []

    #     # ---------------- JOURNAL ENTRY ---------------- #
    #     from decimal import Decimal

    #     invoice_obj = SaleInvoiceOrders.objects.get(sale_invoice_id=sale_invoice_id)
    #     invoice_obj.pending_amount = invoice_obj.total_amount
    #     invoice_obj.save(update_fields=['pending_amount'])

    #     existing_balance = (
    #         JournalEntryLines.objects
    #         .filter(customer_id=invoice_obj.customer_id)
    #         .order_by('is_deleted', '-created_at')
    #         .values_list('balance', flat=True)
    #         .first()
    #     ) or Decimal('0.00')

    #     new_balance = Decimal(existing_balance) + Decimal(invoice_obj.total_amount)
    #     sale_account = LedgerAccounts.objects.get(name__iexact="Sale Account")

    #     invoice_items_qs = SaleInvoiceItems.objects.filter(sale_invoice_id=sale_invoice_id)
    #     product_lines = [
    #         f"{idx}) {item.product_id.name} – Qty: {item.quantity:.2f} @ {item.rate:.2f}"
    #         for idx, item in enumerate(invoice_items_qs, start=1)
    #     ]

    #     description = (
    #         f"Goods sold to {invoice_obj.customer_id.name}\n" +
    #         "\n".join(product_lines)
    #     )

    #     JournalEntryLines.objects.create(
    #         ledger_account_id=sale_account,
    #         debit=invoice_obj.total_amount,
    #         credit=Decimal('0.00'),
    #         voucher_no=invoice_obj.invoice_no,
    #         description=description,
    #         customer_id=invoice_obj.customer_id,
    #         balance=new_balance
    #     )

    #     # ---------------- RESPONSE ---------------- #
    #     custom_data = {
    #         "sale_invoice_order": new_invoice_data,
    #         "sale_invoice_items": invoice_items,
    #         "order_attachments": order_attachments,
    #         "order_shipments": order_shipments,
    #         "custom_field_values": custom_fields
    #     }

    #     log_user_action(
    #         using_db,
    #         request.user,
    #         "CREATE",
    #         "Sale Invoice",
    #         sale_invoice_id,
    #         f"{sale_invoice_data.get('invoice_no')} - Sale Invoice Created"
    #     )

    #     return build_response(
    #         1,
    #         "Sale Invoice created successfully",
    #         custom_data,
    #         status.HTTP_201_CREATED
    #     )



    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        # ------------------------------ C H E C K  D A T A B A S E ------------------------------ #
        db_to_use = None
        errors = {}
        try:
            # Check in mstcnl DB
            MstcnlSaleInvoiceOrder.objects.using('mstcnl').get(sale_invoice_id=pk)
            # Instead of update, return custom response
            return build_response(
                0,
                "Update is not allowed, please contact Product team.",
                errors,
                status.HTTP_400_BAD_REQUEST
            )

        except ObjectDoesNotExist:
            try:
                # Check if sale_invoice_id exists in the default (devcnl) database
                SaleInvoiceOrders.objects.using('default').get(sale_invoice_id=pk)
                set_db('default')
                db_to_use = 'default'
                # keep using default models + serializers
            except ObjectDoesNotExist:
                logger.error(f"Sale Invoice Order with id {pk} not found in any database.")
                return build_response(0, f"Sale Invoice order with id {pk} not found", [], status.HTTP_404_NOT_FOUND)

        # ------------------------------ D A T A   V A L I D A T I O N ------------------------------ #
        given_data = request.data

        # Validate SaleInvoiceOrders Data
        sale_invoice_order_data = given_data.pop('sale_invoice_order', None)
        if sale_invoice_order_data:
            sale_invoice_order_data['sale_invoice_id'] = pk
            order_error = validate_multiple_data(self, [sale_invoice_order_data], SaleInvoiceOrdersSerializer, ['invoice_no'], using_db=db_to_use)
            validate_order_type(sale_invoice_order_data, order_error, OrderTypes, look_up='order_type')
        
        # Validate SaleInvoiceItems Data
        sale_invoice_items_data = given_data.pop('sale_invoice_items', None)
        
        # ------------------ IMPORTANT NEW LOGIC ------------------ #
        # Filter out empty UI rows (only keep rows with real product)
        if sale_invoice_items_data:
            sale_invoice_items_data = [
                item for item in sale_invoice_items_data
                if item.get("product_id") and item.get("quantity")
            ]
        #-----------------------------------------------------------------------
        if sale_invoice_items_data:
            exclude_fields = ['sale_invoice_id']
            item_error = validate_put_method_data(self, sale_invoice_items_data, SaleInvoiceItemsSerializer, exclude_fields, SaleInvoiceItems, current_model_pk_field='sale_invoice_item_id', db_to_use=db_to_use)
        else:
            item_error = []

        # Validate OrderAttachments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id', 'order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id', db_to_use=db_to_use)
        else:
            attachment_error = []

        # Validate OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id', db_to_use=db_to_use)
        else:
            shipments_error = []

        # Validate CustomFieldValues Data
        custom_field_values_data = given_data.pop('custom_field_values', None)
        if custom_field_values_data:
            exclude_fields = ['custom_id']
            custom_field_values_error = validate_put_method_data(self, custom_field_values_data, CustomFieldValueSerializer, exclude_fields, CustomFieldValue, current_model_pk_field='custom_field_value_id', db_to_use=db_to_use)
        else:
            custom_field_values_error = []

        # Ensure mandatory data is present
        if not sale_invoice_order_data or not sale_invoice_items_data:
            logger.error("Sale invoice order and sale invoice items & CustomFields are mandatory but not provided.")
            return build_response(0, "Sale order and sale order items & CustomFields are mandatory", [], status.HTTP_400_BAD_REQUEST)

        # Collect all errors
        
        if order_error:
            errors["sale_invoice_order"] = order_error
        if item_error:
            errors["sale_invoice_items"] = item_error
        if attachment_error:
            errors["order_attachments"] = attachment_error
        if shipments_error:
            errors["order_shipments"] = shipments_error
        if custom_field_values_error:
            errors["custom_field_values"] = custom_field_values_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N ------------------------------ #

        order_type_val = sale_invoice_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        if not order_type:
            logger.error(f"Order type '{order_type_val}' not found in OrderTypes.")
            return build_response(0, f"Invalid order_type '{order_type_val}' provided", [], status.HTTP_400_BAD_REQUEST)

        type_id = order_type.order_type_id
        
        if sale_invoice_order_data:
            update_fields = []
            sale_invoice_order_data = update_multi_instances(
                self, pk, sale_invoice_order_data, SaleInvoiceOrders, SaleInvoiceOrdersSerializer,
                update_fields, main_model_related_field='sale_invoice_id',
                current_model_pk_field='sale_invoice_id', using_db=db_to_use
            )
            sale_invoice_order_data = sale_invoice_order_data[0] if len(sale_invoice_order_data) == 1 else sale_invoice_order_data
        
        # Update SaleInvoiceItems
        update_fields = {'sale_invoice_id': pk}
        invoice_items_data = update_multi_instances(
            self, pk, sale_invoice_items_data, SaleInvoiceItems, SaleInvoiceItemsSerializer,
            update_fields, main_model_related_field='sale_invoice_id',
            current_model_pk_field='sale_invoice_item_id', using_db=db_to_use
        )

        # Update OrderAttachments
        update_fields = {'order_id': pk, 'order_type_id': type_id}
        attachment_data = update_multi_instances(
            self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer,
            update_fields, main_model_related_field='order_id',
            current_model_pk_field='attachment_id', using_db=db_to_use
        )

        # Update OrderShipments
        shipment_data = update_multi_instances(
            self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer,
            update_fields, main_model_related_field='order_id',
            current_model_pk_field='shipment_id', using_db=db_to_use
        )
        shipment_data = shipment_data[0] if len(shipment_data) == 1 else shipment_data

        # Update CustomFieldValues
        if custom_field_values_data:
            custom_field_values_data = update_multi_instances(
                self, pk, custom_field_values_data, CustomFieldValue, CustomFieldValueSerializer,
                {}, main_model_related_field='custom_id',
                current_model_pk_field='custom_field_value_id', using_db=db_to_use
            )

        # Build Response
        custom_data = {
            "sale_invoice_order": sale_invoice_order_data,
            "sale_invoice_items": invoice_items_data if invoice_items_data else [],
            "order_attachments": attachment_data if attachment_data else [],
            "order_shipments": shipment_data if shipment_data else {},
            "custom_field_values": custom_field_values_data if custom_field_values_data else []
        }
        
        saleinvoice_no = sale_invoice_order_data.get("invoice_no")
        
        # Log the Create
        log_user_action(
            db_to_use,
            request.user,
            "UPDATE",
            "Sale Invoice",
            pk,
            f"{saleinvoice_no} - Sale Invoice Record Updated by {request.user.username}"
        )

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)


from decimal import Decimal

def create_sale_invoice_journal_entry(instance):
    # Existing balance
    existing_balance = (
        JournalEntryLines.objects
        .filter(customer_id=instance.customer_id)
        .order_by('is_deleted', '-created_at')
        .values_list('balance', flat=True)
        .first()
    ) or Decimal('0.00')

    new_balance = Decimal(existing_balance) + Decimal(instance.total_amount)

    sale_account = LedgerAccounts.objects.get(name__iexact="Sale Account")

    # -------- FETCH ITEMS (CORRECT WAY) --------
    invoice_items = SaleInvoiceItems.objects.filter(
        sale_invoice_id=instance.sale_invoice_id
    )

    product_lines = []
    for idx, item in enumerate(invoice_items, start=1):
        product_lines.append(
            f"{idx}) {item.print_name} – Qty: {item.quantity} @ {item.rate}"
        )

    products_description = "\n".join(product_lines)

    description = (
        f"Goods sold to {instance.customer_id.name}"
        f"{products_description}"
    )

    JournalEntryLines.objects.create(
        ledger_account_id=sale_account,
        debit=instance.total_amount,
        credit=0.00,
        voucher_no=instance.invoice_no,
        description=description,
        customer_id=instance.customer_id,
        balance=new_balance
    )

def replicate_invoice_to_mstcnl(sale_invoice_id):
    try:
        source_db = 'default'
        target_db = 'mstcnl'

        invoice = SaleInvoiceOrders.objects.using(source_db).get(sale_invoice_id=sale_invoice_id)
        invoice_items = SaleInvoiceItems.objects.using(source_db).filter(sale_invoice_id=sale_invoice_id)
        order_attachments = OrderAttachments.objects.using(source_db).filter(order_id=sale_invoice_id)
        order_shipments = OrderShipments.objects.using(source_db).filter(order_id=sale_invoice_id)

        # Replicate sale_invoice_order
        invoice_data = model_to_dict(invoice)
        invoice_data.pop('id', None)
        SaleInvoiceOrders.objects.using(target_db).create(**invoice_data)

        # Replicate sale_invoice_items
        new_items = [SaleInvoiceItems(**{**model_to_dict(i), 'id': None}) for i in invoice_items]
        SaleInvoiceItems.objects.using(target_db).bulk_create(new_items)

        # Replicate order_attachments
        new_attachments = [OrderAttachments(**{**model_to_dict(a), 'id': None}) for a in order_attachments]
        OrderAttachments.objects.using(target_db).bulk_create(new_attachments)

        # Replicate order_shipments
        new_shipments = [OrderShipments(**{**model_to_dict(s), 'id': None}) for s in order_shipments]
        OrderShipments.objects.using(target_db).bulk_create(new_shipments)

        logger.info(f"Sale invoice {sale_invoice_id} replicated to mstcnl DB.")
    except Exception as e:
        logger.error(f"Error replicating invoice to mstcnl: {str(e)}")


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
                salereturnorders = SaleReturnOrders.objects.all().order_by('is_deleted', '-created_at')
                data = SaleReturnOrdersOptionsSerializer.get_sale_return_orders_summary(salereturnorders)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
             
            logger.info("Retrieving all sale return order")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            
            queryset = SaleReturnOrders.objects.all().order_by('is_deleted', '-created_at')

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
        Handles the cancellation of a Sale Return order:
        - Marks it as 'Cancelled' instead of deleting
        - If Damaged: no inventory update, no ledger entry
        - If Wrong Product: revert inventory + create reversal ledger entry
        """
        try:
            # --- Step 1: Get the SaleReturnOrders instance
            instance = SaleReturnOrders.objects.get(pk=pk)

            # --- Step 2: Get or verify the 'Cancelled' status
            try:
                canceled_status = OrderStatuses.objects.get(status_name='Cancelled')
            except OrderStatuses.DoesNotExist:
                logger.error("'Cancelled' status not found in OrderStatuses table")
                return build_response(0, "Cannot cancel sale return - required status not found", [], status.HTTP_400_BAD_REQUEST)

            # --- Step 3: Mark the return as Cancelled
            instance.order_status_id = canceled_status
            instance.save()

            return_reason = getattr(instance, 'return_reason', None)
            invoice_no = getattr(instance, 'return_no', None)
            customer_id = instance.customer_id

            logger.info(f"Sale Return {invoice_no} marked as Cancelled (Reason: {return_reason})")

            # --- Step 4: Handle based on reason
            if return_reason and return_reason.lower() == 'damaged':
                # Skip inventory update & ledger action
                logger.info(f"Skipping inventory and ledger actions for damaged return {invoice_no}")

            elif return_reason and return_reason.lower() == 'wrong product':
                # --- Step 4a: Revert products back to inventory
                try:
                    return_items = SaleReturnItems.objects.filter(sale_return_id=instance.sale_return_id)
                    for item in return_items:
                        product = item.product_id  # FK to Product
                        product.balance = F('balance') + item.quantity
                        product.save()

                    logger.info(f"Reverted {len(return_items)} products to inventory for cancelled return {invoice_no}")
                    # Log the Create
                    log_user_action(
                        set_db('default'),
                        request.user,
                        "RETURN",
                        "Sale Return",
                        pk,
                        f"{instance.return_no} - products Reverted to inventory for cancelled"
                    )
                except Exception as e:
                    logger.error(f"Error reverting products to inventory for return {invoice_no}: {str(e)}")

                # --- Step 4b: Create reversing ledger entry
                try:
                    existing_balance = (
                        JournalEntryLines.objects.filter(customer_id=customer_id)
                        .order_by('is_deleted', '-created_at')
                        .values_list('balance', flat=True)
                        .first()
                    ) or Decimal('0.00')

                    latest_balance = existing_balance - Decimal(instance.total_amount)

                    JournalEntryLines.objects.create(
                        description=f"Cancellation of sale return {invoice_no}",
                        credit=instance.total_amount,
                        debit=0,
                        voucher_no=invoice_no,
                        customer_id=customer_id,
                        balance=latest_balance
                    )

                    logger.info(f"Created reversal ledger entry for cancelled sale return {invoice_no}")
                except Exception as e:
                    logger.error(f"Error creating ledger reversal entry for return {invoice_no}: {str(e)}")

            else:
                logger.warning(f"Unknown or missing return reason for sale return {invoice_no}. No additional actions taken.")

            # --- Step 5: Success response
            return build_response(1, "Sale Return cancelled successfully", [], status.HTTP_200_OK)

        except SaleReturnOrders.DoesNotExist:
            logger.warning(f"SaleReturnOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error cancelling SaleReturnOrders with ID {pk}: {str(e)}")
            return build_response(0, "Sale return cancellation failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted SaleReturnOrders record (is_deleted=True → is_deleted=False).
        """
        try:
            instance = SaleReturnOrders.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"SaleReturnOrders with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save() 
            
            # Log the Create
            log_user_action(
                set_db,
                request.user,
                "RESTORED",
                "Sale Returns",
                pk,
                f"{instance.return_no} - Sale Returns Record Restored by {request.user.username}"
            ) 

            logger.info(f"SaleReturnOrders with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except SaleReturnOrders.DoesNotExist:
            logger.warning(f"SaleReturnOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring SaleReturnOrders with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        db_name = set_db('default')
        # Vlidated SaleReturnOrders Data
        sale_return_order_data = given_data.pop('sale_return_order', None)  # parent_data
        sale_return_items_data = given_data.pop('sale_return_items', None)
        
        # ---------------- CLEAN EMPTY SALE ORDER ITEMS ---------------- #
        # Remove blank/empty payloads created by frontend (5 default rows)
        # 👉 ADD THIS BELOW
        sale_return_items_data = [
            item for item in sale_return_items_data
            if item.get("product_id") and item.get("quantity")
        ]
        #----------------------------------------------------------

        if sale_return_order_data:
            order_error = validate_payload_data(
                self, sale_return_order_data, SaleReturnOrdersSerializer, using=db_name)
            # validate the order_type in 'sale_return_order' data
            validate_order_type(sale_return_order_data, order_error,
                                OrderTypes, look_up='order_type')

        # Vlidated SaleReturnItems Data
        
        if sale_return_items_data:
            item_error = validate_multiple_data(
                self, sale_return_items_data, SaleReturnItemsSerializer, ['sale_return_id'], using_db=db_name)

        # Vlidated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(
                self, order_attachments_data, OrderAttachmentsSerializer, ['order_id', 'order_type_id'], using_db=db_name)
        else:
            # Since 'order_attachments' is optional, so making an error is empty list
            attachment_error = []

        # Vlidated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_multiple_data(
                self, [order_shipments_data], OrderShipmentsSerializer, ['order_id', 'order_type_id'], using_db=db_name)
        else:
            # Since 'order_shipments' is optional, so making an error is empty list
            shipments_error = []
            
        # Validate Custom Fields Data
        custom_fields_data = given_data.pop('custom_field_values', None)
        if custom_fields_data:
            custom_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'], using_db=db_name)
        else:
            custom_error = []

        # Ensure mandatory data is present
        if not sale_return_order_data or not sale_return_items_data:
            logger.error(
                "Sale return order and sale return items & CustomFields are mandatory but not provided.")
            return build_response(0, "Sale return order and sale return items & CustomFields are mandatory", [], status.HTTP_400_BAD_REQUEST)

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
        new_sale_return_order_data = generic_data_creation(self, [sale_return_order_data], SaleReturnOrdersSerializer, using=db_name)
        new_sale_return_order_data = new_sale_return_order_data[0]
        sale_return_id = new_sale_return_order_data.get("sale_return_id", None)  # Fetch sale_return_id from mew instance
        logger.info('SaleReturnOrders - created*')

        # Create SaleReturnItems Data
        update_fields = {'sale_return_id': sale_return_id}
        items_data = generic_data_creation(
            self, sale_return_items_data, SaleReturnItemsSerializer, update_fields, using=db_name)
        logger.info('SaleReturnItems - created*')

        # Get order_type_id from OrderTypes model
        order_type_val = sale_return_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id': sale_return_id, 'order_type_id': type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(
                self, order_attachments_data, OrderAttachmentsSerializer, update_fields, using=db_name)
            logger.info('OrderAttchments - created*')
        else:
            # Since OrderAttchments Data is optional, so making it as an empty data list
            order_attachments = []

        # create OrderShipments Data
        if order_shipments_data:
            order_shipments = generic_data_creation(
                self, [order_shipments_data], OrderShipmentsSerializer, update_fields, using=db_name)
            order_shipments = order_shipments[0]
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = {}
            
        # Assign `custom_id = vendor_id` for CustomFieldValues
        if custom_fields_data:
            update_fields = {'custom_id': sale_return_id}  # Now using `custom_id` like `order_id`
            custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, update_fields, using=db_name)
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
        
        returnno = sale_return_order_data.get("return_no")
        # Log the Create
        log_user_action(
            db_name,
            request.user,
            "CREATE",
            "Sale Returns",
            sale_return_id,
            f"{returnno} - Sale Returns Record Created by {request.user.username}"
        )

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
        # ------------------ IMPORTANT NEW LOGIC ------------------ #
        # Filter out empty UI rows (only keep rows with real product)
        if sale_return_items_data:
            sale_return_items_data = [
                item for item in sale_return_items_data
                if item.get("product_id") and item.get("quantity")
            ]
            
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
                "Sale return order and sale return items & CustomFields are mandatory but not provided.")
            return build_response(0, "Sale return order and sale return items & CustomFields are mandatory", [], status.HTTP_400_BAD_REQUEST)

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
        
        returnno = sale_return_order_data.get("return_no")
        # Log the Create
        log_user_action(
            set_db("default"),
            request.user,
            "UPDATE",
            "Sale Returns",
            pk,
            f"{returnno} - Sale Returns Record Updated by {request.user.username}"
        )

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

            queryset = QuickPacks.objects.all().order_by('is_deleted', '-created_at')	

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
            # instance.delete()
            instance.is_deleted = True
            instance.save()

            logger.info(f"QuickPacks with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except QuickPacks.DoesNotExist:
            logger.warning(f"QuickPacks with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting QuickPacks with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted QuickPacks record (is_deleted=True → is_deleted=False).
        """
        try:
            instance = QuickPacks.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"QuickPacks with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save()

            logger.info(f"QuickPacks with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except QuickPacks.DoesNotExist:
            logger.warning(f"QuickPacks with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring QuickPacks with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

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
        quick_pack_items_data = [
            item for item in quick_pack_items_data
            if item.get("product_id") and item.get("quantity")
        ]
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
        
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "CREATE",
            "Quick Pack",
            quick_pack_id,
            f"{quick_pack_id} - Quick Pack Record Created by {request.user.username}"
        )

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
        
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "UPDATE",
            "Quick Pack",
            pk,
            f"{pk} - Quick Pack Record Updated by {request.user.username}"
        )

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

def sale_invoice_exists_in_db(sale_invoice_id, db):
        try:
            return SaleInvoiceOrders.objects.using(db).filter(sale_invoice_id=sale_invoice_id).exists()
        except Exception as e:
            return False
        
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

            queryset = SaleReceipt.objects.all().order_by('is_deleted', '-created_at')	

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

    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        #print("-"*20)
        #print("We entered in create mode...")
        # Extracting data from the request
        given_data = request.data
        #print("given_data : ", given_data)
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
        
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "CREATE",
            "SALE RECEIPT",
            sale_receipt_id,
            f"{sale_receipt_id} - Sale Receipt Record Created by {request.user.username}"
        )

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
        
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "UPDATE",
            "SALE RECEIPT",
            pk,
            f"{pk} - Sale Receipt Record Updated by {request.user.username}"
        )

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

            queryset = Workflow.objects.all().order_by('is_deleted', '-created_at')

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
            
            # Soft delete related WorkflowStages
            WorkflowStage.objects.filter(workflow_id=pk).update(is_deleted=True)
            # instance.delete()
            
            # Soft delete the Workflow
            instance.is_deleted = True
            instance.save()

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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class SaleReceiptViewSet(viewsets.ModelViewSet):
    queryset = SaleReceipt.objects.all()
    serializer_class = SaleReceiptSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = SaleReceiptFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        data = request.data
        db_alias = None

        if isinstance(data, dict) and 'sale_invoice_id' in data:
            sale_invoice_id = data.get('sale_invoice_id')

            if sale_invoice_exists_in_db(sale_invoice_id, 'default'):
                db_alias = 'default'
            elif sale_invoice_exists_in_db(sale_invoice_id, 'mstcnl'):
                db_alias = 'mstcnl'
            else:
                return build_response(0, f"sale_invoice_id {sale_invoice_id} not found in either DB", [], status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data, context={'db_alias': db_alias})

        if serializer.is_valid():
            instance = serializer.save()
            data = self.get_serializer(instance).data
            return build_response(1, "Record created successfully", data, status.HTTP_201_CREATED)
        else:
            errors_str = json.dumps(serializer.errors, indent=2)
            logger.error("Serializer validation error: %s", errors_str)
            return build_response(0, "Form validation failed", [], errors=serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)


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
        #print("Hello")
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all salecreditnote")
            #print("try block is triggering")
            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10))
            
            queryset = SaleCreditNotes.objects.all().order_by('is_deleted', '-created_at')	
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
            instance.is_deleted=True 
            instance.save()

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
        #print("Create is running now:")
        # Extracting data from the request
        given_data = request.data

        db_name = set_db('default')
        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        # Vlidated SaleOrder Data
        sale_credit_note_data = given_data.pop('sale_credit_note', None)  # parent_data
        if sale_credit_note_data:
            credit_note_error = validate_payload_data(
                self, sale_credit_note_data, SaleCreditNoteSerializers, using=db_name)

        # Vlidated SaleOrderItems Data
        # sale_credit_items_data = given_data.pop('sale_credit_note_items', None)
        # if sale_credit_items_data:
        #     item_error = validate_multiple_data(
        #         self, sale_credit_items_data, SaleCreditNoteItemsSerializers, ['credit_note_id'], using_db=db_name)

        # Ensure mandatory data is present
        # if not sale_credit_note_data or not sale_credit_items_data:
        #     logger.error("SaleCreditNote and SaleCreditNote items are mandatory but not provided.")
        #     return build_response(0, "SaleCreditNote and SaleCreditNote items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if credit_note_error:
            errors["sale_credit_note"] = credit_note_error
        # if item_error:
        #     errors["sale_credit_note_items"] = item_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create SaleCreditNotes Data
        new_sale_credit_note_data = generic_data_creation(self, [sale_credit_note_data], SaleCreditNoteSerializers, using=db_name)
        new_sale_credit_note_data = new_sale_credit_note_data[0]
        credit_note_id = new_sale_credit_note_data.get("credit_note_id", None)
        logger.info('SaleCreditNotes - created*')

        # Create SaleCreditNotesItems Data
        update_fields = {'credit_note_id': credit_note_id}
        # items_data = generic_data_creation(
        #     self, sale_credit_items_data, SaleCreditNoteItemsSerializers, update_fields, using=db_name)
        logger.info('SaleCreditNotesItems - created*')


        custom_data = {
            "sale_credit_note": new_sale_credit_note_data,
            # "sale_credit_note_items": items_data,
        }
        
        creditno = sale_credit_note_data.get("credit_note_number")
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "CREATE",
            "CREDIT NOTE",
            credit_note_id,
            f"{creditno} - Credit Note Record Created by {request.user.username}"
        )

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
        # sale_credit_items_data = given_data.pop('sale_credit_note_items', None)
        # if sale_credit_items_data:
        #     exclude_fields = ['credit_note_id']
        #     item_error = validate_put_method_data(self, sale_credit_items_data, SaleCreditNoteItemsSerializers,
        #                                           exclude_fields, SaleCreditNoteItems, current_model_pk_field='credit_note_item_id')

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
        # if not sale_credit_note_data or not sale_credit_items_data:
        #     logger.error(
        #         "SaleCreditNote and SaleCreditNote items are mandatory but not provided.")
        #     return build_response(0, "SaleCreditNote and SaleCreditNote items are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if credit_note_error:
            errors["sale_credit_note"] = credit_note_error
        # if item_error:
        #     errors["sale_credit_note_items"] = item_error
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
        # items_data = update_multi_instances(self, pk, sale_credit_items_data, SaleCreditNoteItems, SaleCreditNoteItemsSerializers,
        #                                     update_fields, main_model_related_field='credit_note_id', current_model_pk_field='credit_note_item_id')

        custom_data = {
            "sale_credit_note": salecreditnote_data[0] if salecreditnote_data else {},
            # "sale_credit_note_items": items_data if items_data else []
        }
        
        creditno = sale_credit_note_data.get("credit_note_number")
        
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "UPDATE",
            "CREDIT NOTE",
            pk,
            f"{creditno} - Credit Note Record Updated by {request.user.username}"
        )

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
            #print("try block is triggering")
            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10))
            
            queryset = SaleDebitNotes.objects.all().order_by('is_deleted', '-created_at')	
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
            instance.is_deleted=True 
            instance.save()

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
        #print("Create is running now:")
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

    # def post(self, request, module_name, object_id):
    #     try:
    #         ModelClass = self.get_model_class(module_name)
    #         obj = ModelClass.objects.get(pk=object_id)

    #         # Find the current workflow stage
    #         current_stage = WorkflowStage.objects.filter(flow_status_id=obj.flow_status_id).first()

    #         if not current_stage:
    #             return Response({"error": "Current workflow stage not found."}, status=status.HTTP_404_NOT_FOUND)

    #         # Check for "Production" stage
    #         production_stage = WorkflowStage.objects.filter(
    #             workflow_id=current_stage.workflow_id_id,
    #             flow_status_id__flow_status_name="Production"
    #         ).first()

    #         if current_stage == production_stage:
    #             # If in "Production", move back to Stage 1
    #             next_stage = WorkflowStage.objects.filter(
    #                 workflow_id=current_stage.workflow_id_id,
    #                 stage_order=1
    #             ).first()
    #         else:
    #             # Otherwise, move to the next stage
    #             next_stage = WorkflowStage.objects.filter(
    #                 workflow_id=current_stage.workflow_id_id,
    #                 stage_order__gt=current_stage.stage_order
    #             ).order_by('stage_order').first()

    #         if next_stage:
    #             obj.flow_status_id = next_stage.flow_status_id
    #             obj.save()

    #             return Response({
    #                 "message": f"{module_name} moved to the next stage.",
    #                 "current_stage": current_stage.flow_status_id.flow_status_name,
    #                 "next_stage": next_stage.flow_status_id.flow_status_name
    #             }, status=status.HTTP_200_OK)

    #         return Response({"message": f"{module_name} has reached the final stage."}, status=status.HTTP_200_OK)

    #     except Exception as e:
    #         return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, module_name, object_id):
        try:
            ModelClass = self.get_model_class(module_name)

            # Try to get object from default DB
            try:
                obj = ModelClass.objects.using('default').get(pk=object_id)
                #print("obj 1: ", obj)
                db_used = 'default'
            except ModelClass.DoesNotExist:
                # Try to get object from mstcnl DB
                obj = ModelClass.objects.using('mstcnl').get(pk=object_id)
                #print("obj 2: ", obj)
                db_used = 'mstcnl'

            current_stage = WorkflowStage.objects.using(db_used).filter(flow_status_id=obj.flow_status_id).first()

            if not current_stage:
                return Response({"error": "Current workflow stage not found."}, status=status.HTTP_404_NOT_FOUND)

            production_stage = WorkflowStage.objects.using(db_used).filter(
                workflow_id=current_stage.workflow_id_id,
                flow_status_id__flow_status_name="Production"
            ).first()

            if current_stage == production_stage:
                next_stage = WorkflowStage.objects.using(db_used).filter(
                    workflow_id=current_stage.workflow_id_id,
                    stage_order=1
                ).first()
            else:
                next_stage = WorkflowStage.objects.using(db_used).filter(
                    workflow_id=current_stage.workflow_id_id,
                    stage_order__gt=current_stage.stage_order
                ).order_by('stage_order').first()

            if next_stage:
                obj.flow_status_id = next_stage.flow_status_id
                obj.save(using=db_used)

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
            #print(f"Updating fields for: {module_name} with ID {object_id}")

            # Update fields with the data from the request
            for field, value in request.data.items():
                if hasattr(obj, field):
                    setattr(obj, field, value)
                    #print(f"Updated {field} to {value}")

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
            #print(f"Model {module_name} not found.")
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

        # ---------------------------------------------------------------------
        # 1️⃣ FIX: Handle customer as STRING or OBJECT (your main error)
        # ---------------------------------------------------------------------
        cust_data = data.get('customer')

        if not cust_data:
            return build_response(1, "Customer data is required.", None, status.HTTP_400_BAD_REQUEST)

        # If frontend sends: "customer": "uuid"
        if isinstance(cust_data, str):
            customer_id = cust_data.replace('-', '')
        else:
            customer_id = cust_data.get('customer_id')
            if not customer_id:
                return build_response(1, "Customer ID is required.", None, status.HTTP_400_BAD_REQUEST)
            customer_id = customer_id.replace('-', '')

        # Validate customer_id
        try:
            uuid.UUID(customer_id)
            Customer.objects.get(pk=customer_id)
        except (ValueError, TypeError, Customer.DoesNotExist) as e:
            return build_response(1, "Invalid customer ID format OR Customer does not exist.", str(e), status.HTTP_404_NOT_FOUND)

        # ---------------------------------------------------------------------
        # 2️⃣ FIX: Ledger Account Handling (string or object)
        # ---------------------------------------------------------------------
        ledger_account_data = data.get('ledger_account_id')

        if isinstance(ledger_account_data, str):
            ledger_account_id = ledger_account_data.replace('-', '')
        elif isinstance(ledger_account_data, dict):
            ledger_account_id = ledger_account_data.get("ledger_account_id")
            if not ledger_account_id:
                return build_response(1, "Ledger Account ID is required.", None, status.HTTP_400_BAD_REQUEST)
            ledger_account_id = ledger_account_id.replace('-', '')
        else:
            return build_response(1, "'ledger_account' must be a string or object.", None, status.HTTP_400_BAD_REQUEST)

        try:
            uuid.UUID(ledger_account_id)
            ledger_account = LedgerAccounts.objects.get(pk=ledger_account_id)
        except (ValueError, TypeError, LedgerAccounts.DoesNotExist) as e:
            return build_response(1, "Invalid Ledger Account ID format OR Ledger Account does not exist.", str(e), status.HTTP_404_NOT_FOUND)

        account_id = ledger_account_id  # Final ledger ID used everywhere

        # ---------------------------------------------------------------------
        # Original code from here forward — NOTHING changed
        # ---------------------------------------------------------------------

        description = data.get('description')

        # Fetch Pending, Completed status IDs
        try:
            pending_status = OrderStatuses.objects.get(status_name="Pending").order_status_id
        except ObjectDoesNotExist:
            return build_response(1, "Required order statuses 'Pending' not found.", None, status.HTTP_404_NOT_FOUND)

        # ---------------------------------------------------------------------
        # adjustNow BLOCK (UNCHANGED)
        # ---------------------------------------------------------------------
        if data.get('adjustNow'):
            data_list = request.data
            
            if isinstance(data_list, dict):
                data_list = [data_list]

            results = []

            try:
                with transaction.atomic():
                    for data in data_list:

                        # Validate adjustNow
                        try:
                            input_adjustNow = Decimal(data.get('adjustNow', 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                            if input_adjustNow <= 0:
                                return build_response(0, "Adjust Now Amount Must Be Positive.", None, status.HTTP_406_NOT_ACCEPTABLE)
                        except (ValueError, TypeError):
                            return build_response(0, "Invalid Adjust Now Amount Provided.", None, status.HTTP_406_NOT_ACCEPTABLE)
                        
                        # Fetch sale invoice
                        try:
                            invoice = SaleInvoiceOrders.objects.get(invoice_no=data.get('invoice_no'))
                            total_amount = invoice.total_amount
                            bal_amt = invoice.balance_amount
                        except SaleInvoiceOrders.DoesNotExist:
                            return build_response(1, f"Sale Invoice with invoice no '{data.get('invoice_no')}' does not exist.", None, status.HTTP_404_NOT_FOUND)
                        
                        # Invoice not completed
                        if invoice.order_status_id.status_name != "Completed":

                            if Decimal(bal_amt).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP) == Decimal(data.get('outstanding_amount', 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP):

                                try:
                                    outstanding_amount = Decimal(data.get('outstanding_amount', 0))
                                except (ValueError, TypeError):
                                    return build_response(0, "Invalid Outstanding Amount Provided.", None, status.HTTP_406_NOT_ACCEPTABLE)

                                if outstanding_amount == 0:
                                    return build_response(0, "No Outstanding Amount", None, status.HTTP_400_BAD_REQUEST)

                                # Allocate payment
                                if input_adjustNow > outstanding_amount:
                                    allocated_amount = outstanding_amount
                                    new_outstanding = Decimal("0.00")
                                    remaining_payment = input_adjustNow - outstanding_amount
                                else:
                                    allocated_amount = input_adjustNow
                                    new_outstanding = outstanding_amount - input_adjustNow
                                    remaining_payment = Decimal("0.00")

                                # Create Payment Transaction
                                customer_instance = Customer.objects.get(pk=customer_id)
                                ledger_account_instance = LedgerAccounts.objects.get(pk=account_id)

                                payment_transaction = PaymentTransactions.objects.create(
                                    payment_receipt_no=data.get('payment_receipt_no'),
                                    payment_method=data.get('payment_method'),
                                    total_amount=total_amount,
                                    outstanding_amount=new_outstanding,
                                    adjusted_now=allocated_amount,
                                    payment_status=data.get('payment_status'),
                                    sale_invoice=invoice,
                                    invoice_no=invoice.invoice_no,
                                    customer=customer_instance,
                                    ledger_account_id=ledger_account_instance
                                )
                                
                                # Log ONLY when created successfully
                                if new_outstanding == 0:
                                    log_user_action(
                                        set_db('default'),
                                        request.user,
                                        "CREATE & UPDATE",
                                        "Payment Transactions & Sale Invoice",
                                        invoice.sale_invoice_id,
                                        f"{payment_transaction.payment_receipt_no} - Payment transaction record created & {invoice.invoice_no} - Invoice marked as Completed by {request.user.username}"
                                    )
                                else:
                                    log_user_action(
                                        set_db('default'),
                                        request.user,
                                        "CREATE",
                                        "Payment Transaction",
                                        payment_transaction.transaction_id,
                                        f"{payment_transaction.payment_receipt_no} - Payment created by {request.user.username}"
                                    )

                                # Update Completed if needed
                                completed_status = OrderStatuses.objects.using('default').filter(status_name='Completed').first()
                                if completed_status:
                                    SaleInvoiceOrders.objects.filter(
                                        sale_invoice_id=invoice.sale_invoice_id
                                    ).update(order_status_id=completed_status.order_status_id)

                                    PaymentTransactions.objects.filter(
                                        sale_invoice_id=invoice.sale_invoice_id
                                    ).update(payment_status="Completed")

                                    replicate_sale_invoice_to_mstcnl(invoice.sale_invoice_id)

                            else:
                                return build_response(0, f"Wrong outstanding_amount. Correct is {bal_amt}", None, status.HTTP_400_BAD_REQUEST)
                        else:
                            return build_response(0, "Invoice Already Completed", None, status.HTTP_400_BAD_REQUEST)

                        # Journal entries
                        journal_entry_line_response = JournalEntryLinesAPIView.post(
                            self, customer_id, account_id, input_adjustNow, description,
                            remaining_payment, data.get('payment_receipt_no')
                        )

                        customer_balance_response = CustomerBalanceView.post(
                            self, request, customer_id, remaining_payment
                        )

                        results.append({
                            "Transaction ID": str(payment_transaction.transaction_id),
                            "Total Invoice Amount": str(total_amount),
                            "Allocated Amount To Invoice": str(allocated_amount),
                            "New Outstanding": str(new_outstanding),
                            "Payment Receipt No": payment_transaction.payment_receipt_no,
                            "Remaining Payment": str(remaining_payment),
                            "account_id": str(account_id),
                            "journal_entry_line": journal_entry_line_response.data.get("message"),
                            "customer_balance": customer_balance_response.data.get("message")
                        })

            except Exception as e:
                traceback.print_exc(e)
                return build_response(1, "An error occurred", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

            return build_response(len(results), "Payment transactions processed successfully", results, status.HTTP_201_CREATED)

        # ---------------------------------------------------------------------
        # AMOUNT (normal flow) BLOCK — UNCHANGED
        # ---------------------------------------------------------------------
        try:
            input_amount = Decimal(data.get('amount', 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
            if input_amount <= 0:
                return build_response(1, "Amount must be positive", None, status.HTTP_406_NOT_ACCEPTABLE)
        except (ValueError, TypeError):
            return build_response(1, "Invalid amount provided.", None, status.HTTP_406_NOT_ACCEPTABLE)

        invoices = SaleInvoiceOrders.objects.filter(customer_id=customer_id).exclude(order_status_id__status_name__in=["Completed", "Cancelled"]).order_by('invoice_date')  # Oldest invoice first
        if not invoices.exists():
            return build_response(0, "No pending invoices found for this customer.", None, status.HTTP_400_BAD_REQUEST)
        remaining_amount = input_amount
        payment_transactions_created = []

        # Get pending invoices
        pending_invoices = SaleInvoiceOrders.objects.filter(
            customer_id=customer_id,
            order_status_id=pending_status
        ).order_by('invoice_date')

        pending_invoice_ids = pending_invoices.values_list('sale_invoice_id', flat=True)

        invoices_with_partial_payments = PaymentTransactions.objects.filter(
            sale_invoice_id__in=pending_invoice_ids,
            customer_id=customer_id
        ).values('sale_invoice_id').annotate(total_paid=Sum('amount')).order_by('sale_invoice_id')

        invoice_dict = {inv.sale_invoice_id: inv for inv in pending_invoices}

        for ip in invoices_with_partial_payments:
            sale_invoice_id = ip['sale_invoice_id']
            if sale_invoice_id in invoice_dict:
                invoice_dict[sale_invoice_id].total_paid = ip['total_paid']
            else:
                invoice_dict[sale_invoice_id] = SaleInvoiceOrders.objects.get(sale_invoice_id=sale_invoice_id)
                invoice_dict[sale_invoice_id].total_paid = ip['total_paid']

        invoices_sorted = sorted(invoice_dict.values(), key=lambda x: x.created_at)

        if invoices_sorted:
            with transaction.atomic():
                for sale_invoice in invoices_sorted:

                    if remaining_amount <= 0:
                        break

                    total_paid = getattr(sale_invoice, 'total_paid', Decimal('0.00')) or Decimal('0.00')

                    payment_transaction_latest = PaymentTransactions.objects.filter(
                        sale_invoice_id=sale_invoice.sale_invoice_id
                    ).order_by('-created_at').first()

                    if payment_transaction_latest:
                        current_outstanding = max(payment_transaction_latest.outstanding_amount, Decimal('0.00'))
                    else:
                        current_outstanding = max(sale_invoice.total_amount - total_paid, Decimal('0.00'))

                    if current_outstanding <= 0:
                        continue

                    allocated_amount = min(remaining_amount, current_outstanding)
                    new_outstanding = current_outstanding - allocated_amount
                    remaining_amount -= allocated_amount

                    customer_instance = Customer.objects.get(pk=customer_id)
                    ledger_account_instance = LedgerAccounts.objects.get(pk=account_id)

                    payment_txn = PaymentTransactions.objects.create(
                        payment_receipt_no=data.get('payment_receipt_no'),
                        payment_method=data.get('payment_method'),
                        cheque_no=data.get('cheque_no'),
                        total_amount=sale_invoice.total_amount,
                        amount=allocated_amount,
                        outstanding_amount=new_outstanding,
                        payment_status=data.get('payment_status'),
                        customer=customer_instance,
                        sale_invoice_id=sale_invoice.sale_invoice_id,
                        invoice_no=sale_invoice.invoice_no,
                        ledger_account_id=ledger_account_instance
                    )
                    
                    #log action
                    if new_outstanding == 0:
                        log_user_action(
                            set_db('default'),
                            request.user,
                            "CREATE & UPDATE",
                            "Payment Transactions & Sale Invoice",
                            sale_invoice.sale_invoice_id,
                            f"{payment_txn.payment_receipt_no} - Payment transaction record created & {sale_invoice.invoice_no} - Invoice marked as Completed by {request.user.username}"
                        )
                    else:
                        log_user_action(
                            set_db('default'),
                            request.user,
                            "CREATE",
                            "Payment Transaction",
                            payment_txn.transaction_id,
                            f"{payment_txn.payment_receipt_no} - Payment created by {request.user.username}"
                        )

                    payment_transactions_created.append(payment_txn)

                    if new_outstanding == Decimal('0.00'):
                        completed_status = OrderStatuses.objects.using('default').filter(status_name='Completed').first()

                        if completed_status:
                            SaleInvoiceOrders.objects.filter(
                                sale_invoice_id=sale_invoice.sale_invoice_id
                            ).update(order_status_id=completed_status.order_status_id)

                            PaymentTransactions.objects.filter(
                                sale_invoice_id=sale_invoice.sale_invoice_id
                            ).update(payment_status="Completed")

                            replicate_sale_invoice_to_mstcnl(sale_invoice.sale_invoice_id)

                existing_balance = (
                    JournalEntryLines.objects.filter(customer_id=customer_id)
                    .order_by('is_deleted', '-created_at')
                    .values_list('balance', flat=True)
                    .first()
                ) or Decimal('0.00')

                total_pending = Decimal(existing_balance) - Decimal(input_amount)

                journal_entry_line_response = JournalEntryLinesAPIView.post(
                    self, customer_id, account_id, input_amount, description,
                    total_pending, data.get('payment_receipt_no')
                )

                customer_balance_response = CustomerBalanceView.post(
                    self, request, customer_id, remaining_amount
                )

            response_data = {
                "payment_transactions": [
                    {
                        "Transaction ID": str(txn.transaction_id),
                        "payment Receipt No": txn.payment_receipt_no,
                        "Total Invoice Amount": str(txn.total_amount),
                        "Amount": str(txn.amount),
                        "Outstanding Amount": str(txn.outstanding_amount),
                        "Sale Invoice Id": txn.sale_invoice_id,
                        "Invoice No": txn.invoice_no,
                        "customer_id": str(customer_id),
                        "account_id": str(account_id),
                        "journal_entry_line": journal_entry_line_response.data.get("message"),
                        "customer_balance": customer_balance_response.data.get("message")
                    }
                    for txn in payment_transactions_created
                ],
                "remaining_payment": str(remaining_amount)
            }

            return build_response(len(payment_transactions_created), "Payment transactions processed successfully", response_data, status.HTTP_201_CREATED)

        else:
            return build_response(0, "No pending or outstanding invoices for this customer", None, status.HTTP_400_BAD_REQUEST)

            
    # def get(self, request, customer_id=None):
    #     records_all = request.query_params.get('records_all', 'false').lower() == 'true'

    #     page = int(request.query_params.get('page', 1))
    #     limit = int(request.query_params.get('limit', 10))

    #     if customer_id:
    #         # default db
    #         payment_transactions = PaymentTransactions.objects.filter(
    #             customer_id=customer_id
    #         ).order_by('-created_at')

    #         # secondary db (only if records_all=true)
    #         mstcnl_payment_transactions = []
    #         if records_all:
    #             mstcnl_payment_transactions = MstCnlPaymentTransactions.objects.using('mstcnl').filter(
    #                 customer_id=customer_id
    #             ).order_by('-created_at')

    #         combined = []

    #         if payment_transactions.exists():
    #             serializer_default = PaymentTransactionSerializer(payment_transactions, many=True)
    #             combined.extend(serializer_default.data)

    #         if mstcnl_payment_transactions:
    #             serializer_mstcnl = MstCnlPaymentTransactionsSerializer(mstcnl_payment_transactions, many=True)
    #             combined.extend(serializer_mstcnl.data)

    #         total_count = len(combined)

    #         if not combined:
    #             return filter_response(0, "No payment transactions found for this customer", page, limit, total_count, None, status.HTTP_400_BAD_REQUEST)

    #         return filter_response(len(combined), "Payment Transactions", combined, page, limit, total_count, status.HTTP_200_OK)

    #     else:
    #         # default db
    #         transactions = PaymentTransactions.objects.all()

    #         if request.query_params:
    #             filterset = PaymentTransactionsReportFilter(request.GET, queryset=transactions)
    #             if filterset.is_valid():
    #                 transactions = filterset.qs

    #         # secondary db (only if records_all=true)
    #         mstcnl_transactions = []
    #         if records_all:
    #             mstcnl_transactions = MstCnlPaymentTransactions.objects.using('mstcnl').all()

    #         combined = []

    #         if transactions.exists():
    #             serializer_default = PaymentTransactionSerializer(transactions, many=True)
    #             combined.extend(serializer_default.data)

    #         if mstcnl_transactions:
    #             serializer_mstcnl = MstCnlPaymentTransactionsSerializer(mstcnl_transactions, many=True)
    #             combined.extend(serializer_mstcnl.data)

    #         # ✅ total_count should reflect both DBs when records_all=true
    #         if records_all:
    #             total_count = PaymentTransactions.objects.count() + MstCnlPaymentTransactions.objects.using('mstcnl').count()
    #         else:
    #             total_count = PaymentTransactions.objects.count()

    #         return filter_response(len(combined), "Payment Transactions", combined, page, limit, total_count, status.HTTP_200_OK)
    
#====================================================================================
    def get(self, request, customer_id=None, transaction_id=None):
        records_all = request.query_params.get('records_all', 'false').lower() == 'true'

        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))

        # ✅ CASE 1: FETCH SINGLE RECORD
        if transaction_id:
            try:
                # Try default DB first
                transaction = PaymentTransactions.objects.get(pk=transaction_id)
                serializer = PaymentTransactionSerializer(transaction)
                return build_response(1, "Payment Transaction (Default DB)", serializer.data, status.HTTP_200_OK)
            except PaymentTransactions.DoesNotExist:
                transaction = None

            # Try secondary DB if records_all = true
            if records_all:
                try:
                    transaction_mstcnl = MstCnlPaymentTransactions.objects.using('mstcnl').get(pk=transaction_id)
                    serializer_mstcnl = MstCnlPaymentTransactionsSerializer(transaction_mstcnl)
                    return build_response(1, "Payment Transaction (MSTCNL DB)", serializer_mstcnl.data, status.HTTP_200_OK)
                except MstCnlPaymentTransactions.DoesNotExist:
                    pass

            return build_response(0, "Payment transaction not found.", None, status.HTTP_404_NOT_FOUND)

        # ✅ CASE 2: FETCH MULTIPLE RECORDS (your existing logic)
        if customer_id:
            payment_transactions = PaymentTransactions.objects.filter(
                customer_id=customer_id
            ).order_by( '-created_at')

            mstcnl_payment_transactions = []
            if records_all:
                mstcnl_payment_transactions = MstCnlPaymentTransactions.objects.using('mstcnl').filter(
                    customer_id=customer_id
                ).order_by('-created_at')

            combined = []

            if payment_transactions.exists():
                serializer_default = PaymentTransactionSerializer(payment_transactions, many=True)
                combined.extend(serializer_default.data)

            if mstcnl_payment_transactions:
                serializer_mstcnl = MstCnlPaymentTransactionsSerializer(mstcnl_payment_transactions, many=True)
                combined.extend(serializer_mstcnl.data)

            total_count = len(combined)

            if not combined:
                return filter_response(0, "No payment transactions found for this customer", page, limit, total_count, None, status.HTTP_400_BAD_REQUEST)

            return filter_response(len(combined), "Payment Transactions", combined, page, limit, total_count, status.HTTP_200_OK)

        else:
            transactions = PaymentTransactions.objects.all()

            if request.query_params:
                filterset = PaymentTransactionsReportFilter(request.GET, queryset=transactions)
                if filterset.is_valid():
                    transactions = filterset.qs

            mstcnl_transactions = []
            if records_all:
                mstcnl_transactions = MstCnlPaymentTransactions.objects.using('mstcnl').all()

            combined = []

            if transactions.exists():
                serializer_default = PaymentTransactionSerializer(transactions, many=True)
                combined.extend(serializer_default.data)

            if mstcnl_transactions:
                serializer_mstcnl = MstCnlPaymentTransactionsSerializer(mstcnl_transactions, many=True)
                combined.extend(serializer_mstcnl.data)

            total_count = (
                PaymentTransactions.objects.count() +
                (MstCnlPaymentTransactions.objects.using('mstcnl').count() if records_all else 0)
            )

            return filter_response(len(combined), "Payment Transactions", combined, page, limit, total_count, status.HTTP_200_OK)

#=====================================================================================


    # def get(self, request, customer_id=None):
    #     records_all = request.query_params.get('records_all', 'false').lower() == 'true'

    #     if customer_id:
    #         payment_transactions = PaymentTransactions.objects.filter(customer_id=customer_id).order_by('is_deleted', '-created_at')

    #         mstcnl_payment_transactions = []
    #         if records_all:
    #             mstcnl_payment_transactions = MstCnlPaymentTransactions.objects.using('mstcnl').filter(customer_id=customer_id).order_by('is_deleted', '-created_at')

    #         combined = []
    #         if payment_transactions.exists():
    #             serializer_default = PaymentTransactionSerializer(payment_transactions, many=True)
    #             combined.extend(serializer_default.data)

    #         if mstcnl_payment_transactions:
    #             serializer_mstcnl = MstCnlPaymentTransactionsSerializer(mstcnl_payment_transactions, many=True)
    #             combined.extend(serializer_mstcnl.data)
                
    #         page = int(request.query_params.get('page', 1))
    #         limit = int(request.query_params.get('limit', 10))
    #         total_count = len(combined)

    #         if not combined:
    #             return filter_response(0, "No payment transactions found for this customer", None, status.HTTP_404_NOT_FOUND)

    #         return filter_response(len(combined), "Payment Transactions", combined, page, limit, total_count,  status.HTTP_200_OK)

    #     else:
    #         transactions = PaymentTransactions.objects.all()

    #         if request.query_params:
    #             filterset = PaymentTransactionsReportFilter(request.GET, queryset=transactions)
    #             if filterset.is_valid():
    #                 transactions = filterset.qs

    #         mstcnl_transactions = []
    #         if records_all:
    #             mstcnl_transactions = MstCnlPaymentTransactions.objects.using('mstcnl').all()

    #         combined = []
    #         if transactions.exists():
    #             serializer_default = PaymentTransactionSerializer(transactions, many=True)
    #             combined.extend(serializer_default.data)

    #         if mstcnl_transactions:
    #             serializer_mstcnl = MstCnlPaymentTransactionsSerializer(mstcnl_transactions, many=True)
    #             combined.extend(serializer_mstcnl.data)
                
    #         page = int(request.query_params.get('page', 1))
    #         limit = int(request.query_params.get('limit', 10))
    #         total_count = PaymentTransactions.objects.count()

    #         return filter_response(len(combined), "Payment Transactions", combined, page, limit, total_count, status.HTTP_200_OK)

    def put(self, request, transaction_id):
        with transaction.atomic():                        
            try:
                pending_status = OrderStatuses.objects.get(status_name="Pending")
                completed_status = OrderStatuses.objects.get(status_name="Completed")
            except ObjectDoesNotExist:
                return build_response(1, "Required order statuses 'Pending' or 'Completed' not found.", None, status.HTTP_404_NOT_FOUND)
            
            # Step 1: Get payment_transactions object
            payment_transactions = get_object_or_404(PaymentTransactions, transaction_id=transaction_id)
            old_amount = payment_transactions.amount
            new_amount = Decimal(request.data.get('amount')).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
  
            # Step 2: Get related invoice (Model object, not dict)
            invoice = SaleInvoiceOrders.objects.get(invoice_no=payment_transactions.invoice_no)
            all_txns = PaymentTransactions.objects.filter(invoice_no=invoice.invoice_no)
            total_of_amount = (PaymentTransactions.objects
                                .filter(invoice_no=invoice.invoice_no)
                                .exclude(payment_receipt_no=request.data.get('payment_receipt_no'))
                                .aggregate(total_amount=Sum('amount'))
                                .get('total_amount') or Decimal('0.00')  )
            
            max_allowed = invoice.total_amount - total_of_amount
            if new_amount <= max_allowed:
                # Step 3: Calculate delta
                delta = new_amount - old_amount

                # Step 4: Update transaction
                payment_transactions.amount = new_amount
                payment_transactions.payment_status = request.data.get('payment_status', payment_transactions.payment_status)
                payment_transactions.save()

                # Step 5: Update sale invoice amounts
                paid = all_txns.aggregate(total=Sum('amount'))['total'] or Decimal('0.00')
                invoice.paid_amount = paid
                invoice.pending_amount = invoice.total_amount - paid

                # Step 6: Update latest transaction's outstanding
                latest_txn = all_txns.latest('payment_date')
                latest_txn.outstanding_amount = invoice.pending_amount
                latest_txn.save()

                # Step 7: Update order_status_id from sale_invoice_orders table
                # Step 7: Assign actual model instance
                invoice.order_status_id = completed_status if invoice.pending_amount == 0 else pending_status
                invoice.save()
                
                # Step 8: Return updated data
                response_data = {
                    **request.data,
                    "payment_receipt_no": payment_transactions.payment_receipt_no,
                    "invoice_no": invoice.invoice_no,
                    "paid_amount": invoice.paid_amount,
                    "pending_amount": invoice.pending_amount,
                    "outstanding_amount": latest_txn.outstanding_amount
                }

                #==========*************Updating ACCOUNT LEDGER ENTRY *************==========
                Pay_transactions = PaymentTransactions.objects.filter(
                        payment_receipt_no=payment_transactions.payment_receipt_no
                    ).exclude(
                invoice_no=payment_transactions.invoice_no)
                
                # Fetch ledger account used in original payment
                account_instance = payment_transactions.ledger_account_id

                customer_instance = payment_transactions.customer
                
                existing_balance = (JournalEntryLines.objects.filter(customer_id=customer_instance.customer_id)
                                                                                .order_by('is_deleted', '-created_at')                   # most recent entry first
                                                                                .values_list('balance', flat=True)         # get only the balance field
                                                                                .first() ) or Decimal('0.00')                               # grab the first result
                
                Reversal_of_wrong_entry_balance = old_amount  +  existing_balance

                #Creating JournalEntryLines record for Reversal of wrong entry
                JournalEntryLines.objects.create(
                ledger_account_id=  account_instance,  
                debit=old_amount,
                voucher_no = request.data.get('payment_receipt_no'),
                credit=0.00,
                description=f"Reversal of wrong entry for payment receipt {request.data.get('payment_receipt_no')} - System Generated Entry",
                customer_id=customer_instance,
                balance= Reversal_of_wrong_entry_balance
                )
                time.sleep(1)
                table_addition = Pay_transactions.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
                final_addition = table_addition + new_amount
                total_pending = Decimal(Reversal_of_wrong_entry_balance) - Decimal(new_amount)                

                # Step 3: Creating JournalEntryLines record
                JournalEntryLines.objects.create(
                ledger_account_id=  account_instance,  
                debit=0.00,
                voucher_no = request.data.get('payment_receipt_no'),
                credit=final_addition,
                description=f"Updated payment receipt {request.data.get('payment_receipt_no')} for Invoice {payment_transactions.invoice_no} - revision recorded",
                customer_id=customer_instance,
                balance=total_pending 
                )

                return build_response(1, "Payment Transaction updated successfully", response_data, None, status.HTTP_200_OK)    
            else:
                return build_response(1, f"Overpayment detected. Max allowed: ₹{max_allowed}", None, status.HTTP_422_UNPROCESSABLE_ENTITY)    
 
    # def get(self, request, customer_id = None):
    #     if customer_id:
    #         '''Fetch All Payment Transactions for a Customer'''
    #         payment_transactions = PaymentTransactions.objects.filter(customer_id=customer_id).select_related('sale_invoice').order_by('is_deleted', '-created_at')
            
    #         if not payment_transactions.exists():
    #             return build_response(0, "No payment transactions found for this customer", None, status.HTTP_404_NOT_FOUND) 

    #         try:
    #             serializer = PaymentTransactionSerializer(payment_transactions, many=True)
    #             return build_response(len(serializer.data), "Payment Transactions", serializer.data, status.HTTP_200_OK)
    #         except Exception as e:
    #             return build_response(0, "An error occurred", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)
    #     else:
    #         transactions = PaymentTransactions.objects.all()
    #         if request.query_params:
    #             filterset = PaymentTransactionsReportFilter(request.GET, queryset=transactions)
    #             if filterset.is_valid():
    #                 transactions = filterset.qs  
            
    #         serializer = PaymentTransactionSerializer(transactions, many=True)
    #         return build_response(len(serializer.data), "Payment Transactions", serializer.data, status.HTTP_200_OK)

class FetchSalesInvoicesForPaymentReceiptTable(APIView):
    '''This API is used to fetch all information related to sales invoices for 
        the Payment Receipt. It's related to the Payment Transaction table only.'''
    def get(self, request, customer_id):
        sale_invoice = SaleInvoiceOrders.objects.filter(customer_id=customer_id)
        
        if not sale_invoice.exists():
            return build_response(0, "No sale invoice found for this customer", None, status.HTTP_400_BAD_REQUEST) 

        try:
            serializer = SaleInvoiceOrdersSerializer(sale_invoice, many=True)
            sorted_data = sorted(
                serializer.data,
                key=lambda x: x['created_at']
            )
            return build_response(len(serializer.data), "Sale Invoices", sorted_data, status.HTTP_200_OK)
        except Exception as e:
            return build_response(0, "An error occurred", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


from django.db import transaction
from django.utils import timezone
import time

def replicate_sale_invoice_to_mstcnl(invoice_id):
    #print("---------------: we entered in correct way...")

    try:
        with transaction.atomic():
            #  1) Fetch invoice from default DB
            sale_invoice = SaleInvoiceOrders.objects.using('default').select_related(
                'customer_id', 'order_status_id', 'payment_term_id',
                'gst_type_id', 'order_salesman_id', 'customer_address_id',
                'payment_link_type_id', 'ledger_account_id'
            ).get(pk=invoice_id)


            #print(f"sale_invoice : {model_to_dict(sale_invoice)}")

            #  2) Check conditions
            if sale_invoice.bill_type != 'OTHERS' and sale_invoice.order_status_id != 'Completed':
                return {"message": "Condition not matched — invoice will remain in default DB."}

            #  3) Flatten FKs
            customer_name = sale_invoice.customer_id.name if sale_invoice.customer_id else None
            order_status_name = sale_invoice.order_status_id.status_name if sale_invoice.order_status_id else None
            payment_term_name = sale_invoice.payment_term_id.name if sale_invoice.payment_term_id else None
            gst_type_name = sale_invoice.gst_type_id.name if sale_invoice.gst_type_id else None
            salesman_name = sale_invoice.order_salesman_id.name if sale_invoice.order_salesman_id else None
            ledger_account_name = sale_invoice.ledger_account_id.name if sale_invoice.ledger_account_id else None
            customer_address_id = sale_invoice.customer_address_id.address if sale_invoice.ledger_account_id else None


            #  4) Create in mstcnl DB
            MstcnlSaleInvoiceOrder.objects.using('mstcnl').create(
                sale_invoice_id = sale_invoice.sale_invoice_id,
                bill_type = sale_invoice.bill_type,
                invoice_date = sale_invoice.invoice_date,
                invoice_no = sale_invoice.invoice_no,
                customer_id = customer_name,
                gst_type_id = gst_type_name,
                email = sale_invoice.email,
                ref_no = sale_invoice.ref_no,
                ref_date = sale_invoice.ref_date,
                order_salesman_id = salesman_name,
                customer_address_id = sale_invoice.customer_address_id,
                payment_term_id = payment_term_name,
                due_date = sale_invoice.due_date,
                # payment_link_type_id = payment_link_type,
                remarks = sale_invoice.remarks,
                advance_amount = sale_invoice.advance_amount,
                ledger_account_id = ledger_account_name,
                item_value = sale_invoice.item_value,
                discount = sale_invoice.discount,
                dis_amt = sale_invoice.dis_amt,
                taxable = sale_invoice.taxable,
                tax_amount = sale_invoice.tax_amount,
                cess_amount = sale_invoice.cess_amount,
                transport_charges = sale_invoice.transport_charges,
                round_off = sale_invoice.round_off,
                total_amount = sale_invoice.total_amount,
                vehicle_name = sale_invoice.vehicle_name,
                total_boxes = sale_invoice.total_boxes,
                order_status_id = order_status_name,
                shipping_address = sale_invoice.shipping_address,
                billing_address = sale_invoice.billing_address,
                sale_order_id = str(sale_invoice.sale_order_id),
                tax = sale_invoice.tax,
                paid_amount = sale_invoice.paid_amount,
                # balance_amount = sale_invoice.balance_amount,
                pending_amount = sale_invoice.pending_amount,
                created_at = sale_invoice.created_at,
                updated_at = timezone.now()
            )

            #print(" SaleInvoiceOrder replicated to mstcnl")

            #  5) Copy Items — flatten product/unit/size/color names
            invoice_items = SaleInvoiceItems.objects.using('default').select_related(
                'product_id', 'unit_options_id', 'size_id', 'color_id'
            ).filter(sale_invoice_id=invoice_id)

            for item in invoice_items:
                MstcnlSaleInvoiceItem.objects.using('mstcnl').create(
                    sale_invoice_item_id = item.sale_invoice_item_id,
                    sale_invoice_id = item.sale_invoice_id,
                    product_id = item.product_id.name if item.product_id else None,
                    unit_options_id = item.unit_options_id.unit_name if item.unit_options_id else None,
                    print_name = item.print_name,
                    quantity = item.quantity,
                    total_boxes = item.total_boxes,
                    rate = item.rate,
                    amount = item.amount,
                    tax = item.tax,
                    remarks = item.remarks,
                    discount = item.discount,
                    size_id = item.size_id.size_name if item.size_id else None,
                    color_id = item.color_id.color_name if item.color_id else None,
                    sgst = item.sgst,
                    cgst = item.cgst,
                    igst = item.igst,
                    created_at = item.created_at,
                    updated_at = timezone.now()
                )

            #print(" SaleInvoiceItems replicated to mstcnl")

            #  6) Copy Shipments
            shipments = OrderShipments.objects.using('default').filter(order_id=invoice_id)
            for shipment in shipments:
                MstcnlOrderShipment.objects.using('mstcnl').create(
                    shipment_id = shipment.shipment_id,
                    order_id = shipment.order_id,
                    destination = shipment.destination,
                    shipping_mode_id = shipment.shipping_mode_id,
                    shipping_company_id = shipment.shipping_company_id,
                    shipping_tracking_no = shipment.shipping_tracking_no,
                    shipping_date = shipment.shipping_date,
                    shipping_charges = shipment.shipping_charges,
                    vehicle_vessel = shipment.vehicle_vessel,
                    charge_type = shipment.charge_type,
                    document_through = shipment.document_through,
                    port_of_landing = shipment.port_of_landing,
                    port_of_discharge = shipment.port_of_discharge,
                    no_of_packets = shipment.no_of_packets,
                    weight = shipment.weight,
                    order_type_id = shipment.order_type_id,
                    created_at = shipment.created_at,
                    updated_at = timezone.now()
                )

            #print(" OrderShipments replicated to mstcnl")

            #  7) Copy Attachments
            attachments = OrderAttachments.objects.using('default').select_related('order_type_id').filter(order_id=invoice_id)
            for attachment in attachments:
                MstcnlOrderAttachment.objects.using('mstcnl').create(
                    attachment_id = attachment.attachment_id,
                    order_id = attachment.order_id,
                    attachment_name = attachment.attachment_name,
                    attachment_path = attachment.attachment_path,
                    order_type_id = attachment.order_type_id,
                    created_at = attachment.created_at,
                    updated_at = timezone.now()
                )

            #print(" OrderAttachments replicated to mstcnl")

            #  8) Copy Custom Fields
            custom_fields = CustomFieldValue.objects.using('default').filter(custom_id=invoice_id)
            for cf in custom_fields:
                MstcnlCustomFieldValue.objects.using('mstcnl').create(
                    custom_field_value_id = cf.custom_field_value_id,
                    custom_field_id = cf.custom_field_id,
                    entity_id = cf.entity_id,
                    field_value = cf.field_value,
                    field_value_type = cf.field_value_type,
                    created_at = cf.created_at,
                    updated_at = timezone.now(),
                    custom_id = cf.custom_id
                )
                
            # === ✅ NEW: Copy Payment Transactions ===
            payment_txns = PaymentTransactions.objects.using('default').filter(sale_invoice_id=invoice_id)
            for txn in payment_txns:
                MstCnlPaymentTransactions.objects.using('mstcnl').create(
                    transaction_id=txn.transaction_id,
                    payment_receipt_no=txn.payment_receipt_no,
                    payment_date=txn.payment_date,
                    payment_method=txn.payment_method,
                    cheque_no=txn.cheque_no,
                    amount=txn.amount,
                    outstanding_amount=txn.outstanding_amount,
                    adjusted_now=txn.adjusted_now,
                    payment_status=txn.payment_status,
                    created_at=txn.created_at,
                    updated_at=timezone.now(),
                    sale_invoice_id=txn.sale_invoice.sale_invoice_id,
                    customer_id=txn.customer.name,
                    invoice_no=txn.invoice_no,
                    total_amount=txn.total_amount,
                    account_id=txn.account.account_id
                )

            print(" Payment replicated to mstcnl")
            
            #  9) Replicate related SaleOrder if valid
            if sale_invoice.sale_order_id:
                replicate_sale_order_to_mstcnl(sale_invoice.sale_order_id.sale_order_id)
            else:
                return {"message": "Sale order id is None — Only invoice will replicated in mstcnl DB."}

            print("Completed whole sale invoice and payment transactions in mstcnl")
            #  10) Delete from default DB
            time.sleep(1)

            SaleInvoiceItems.objects.using('default').filter(sale_invoice_id=invoice_id).delete()
            OrderShipments.objects.using('default').filter(order_id=invoice_id).delete()
            OrderAttachments.objects.using('default').filter(order_id=invoice_id).delete()
            CustomFieldValue.objects.using('default').filter(custom_id=invoice_id).delete()
            SaleInvoiceOrders.objects.using('default').filter(pk=invoice_id).delete()

            return {"message": f"Sale Invoice {invoice_id} moved to mstcnl DB successfully"}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}
    
    # finally:
    #     #  Always delete source records
    #     time.sleep(1)
    #     if sale_invoice.bill_type != 'OTHERS' and sale_invoice.order_status_id != 'Completed':
    #         return {"message": "Condition not matched — invoice will remain in default DB."}
    #     else:
    #         SaleInvoiceItems.objects.using('default').filter(sale_invoice_id=invoice_id).delete()
    #         OrderShipments.objects.using('default').filter(order_id=invoice_id).delete()
    #         OrderAttachments.objects.using('default').filter(order_id=invoice_id).delete()
    #         CustomFieldValue.objects.using('default').filter(custom_id=invoice_id).delete()
    #         SaleInvoiceOrders.objects.using('default').filter(pk=invoice_id).delete()
    #         print(" Default DB records deleted.")

    return {"message": f"Sale Invoice {invoice_id} moved to mstcnl DB successfully"}


def replicate_sale_order_to_mstcnl(sale_order_id):
    try:
        with transaction.atomic():
            sale_order = SaleOrder.objects.get(pk=sale_order_id)
            # Flatten FKs
            customer_name = sale_order.customer_id.name if sale_order.customer_id else None
            sale_type_name = sale_order.sale_type_id.name if sale_order.sale_type_id else None
            flow_status_name = sale_order.flow_status_id.flow_status_name if sale_order.flow_status_id else None
            order_status_name = sale_order.order_status_id.status_name if sale_order.order_status_id else None

            #  Check conditions
            if sale_type_name != 'Other' or flow_status_name != 'Completed':
                # #print(f"Conditions not matched for SaleOrder {sale_order_id} → skipping")
                return {"message": "Conditions not matched — SaleOrder not replicated"}

            #  Create in mstcnl DB
            MstcnlSaleOrder.objects.using('mstcnl').create(
                sale_order_id = sale_order.sale_order_id,
                order_no = sale_order.order_no,
                ref_no = sale_order.ref_no,
                ref_date = sale_order.ref_date,
                order_date = sale_order.order_date,
                delivery_date = sale_order.delivery_date,
                customer_id = customer_name,
                sale_type_id = sale_type_name,
                flow_status_id = flow_status_name,
                order_status_id = order_status_name,
                remarks = sale_order.remarks,
                email = sale_order.email,
                total_amount = sale_order.total_amount,
                advance_amount = sale_order.advance_amount,
                item_value = sale_order.item_value,
                tax_amount = sale_order.tax_amount,
                discount = sale_order.discount,
                tax = sale_order.tax,
                sale_estimate = sale_order.sale_estimate,
                use_workflow = sale_order.use_workflow,
                shipping_address = sale_order.shipping_address,
                billing_address = sale_order.billing_address,
                created_at = sale_order.created_at,
                updated_at = timezone.now()
            )

            # #print(f" SaleOrder {sale_order_id} replicated to mstcnl!")

            #  Copy sale_order_items
            sale_order_items = SaleOrderItems.objects.using('default').select_related(
                'product_id', 'unit_options_id', 'size_id', 'color_id'
            ).filter(sale_order_id=sale_order_id)

            for item in sale_order_items:
                MstcnlSaleOrderItem.objects.using('mstcnl').create(
                    sale_order_item_id = item.sale_order_item_id,
                    sale_order_id = sale_order.sale_order_id,
                    product_id = item.product_id.name if item.product_id else None,
                    unit_options_id = item.unit_options_id.unit_name if item.unit_options_id else None,
                    size_id = item.size_id.size_name if item.size_id else None,
                    color_id = item.color_id.color_name if item.color_id else None,
                    quantity = item.quantity,
                    rate = item.rate,
                    amount = item.amount,
                    discount = item.discount,
                    tax = item.tax,
                    cgst = item.cgst,
                    sgst = item.sgst,
                    igst = item.igst,
                    invoiced = item.invoiced,
                    work_order_created = item.work_order_created,
                    remarks = item.remarks,
                    created_at = item.created_at,
                    updated_at = timezone.now()
                )

            # #print(f" SaleOrderItems for {sale_order_id} replicated to mstcnl!")
            
            #  6) Copy Shipments
            shipments = OrderShipments.objects.using('default').filter(order_id=sale_order_id)
            for shipment in shipments:
                MstcnlOrderShipment.objects.using('mstcnl').create(
                    shipment_id = shipment.shipment_id,
                    order_id = shipment.order_id,
                    destination = shipment.destination,
                    shipping_mode_id = shipment.shipping_mode_id,
                    shipping_company_id = shipment.shipping_company_id,
                    shipping_tracking_no = shipment.shipping_tracking_no,
                    shipping_date = shipment.shipping_date,
                    shipping_charges = shipment.shipping_charges,
                    vehicle_vessel = shipment.vehicle_vessel,
                    charge_type = shipment.charge_type,
                    document_through = shipment.document_through,
                    port_of_landing = shipment.port_of_landing,
                    port_of_discharge = shipment.port_of_discharge,
                    no_of_packets = shipment.no_of_packets,
                    weight = shipment.weight,
                    order_type_id = shipment.order_type_id,
                    created_at = shipment.created_at,
                    updated_at = timezone.now()
                )

            # #print(" OrderShipments replicated to mstcnl")

            #  7) Copy Attachments
            attachments = OrderAttachments.objects.using('default').select_related('order_type_id').filter(order_id=sale_order_id)
            for attachment in attachments:
                MstcnlOrderAttachment.objects.using('mstcnl').create(
                    attachment_id = attachment.attachment_id,
                    order_id = attachment.order_id,
                    attachment_name = attachment.attachment_name,
                    attachment_path = attachment.attachment_path,
                    order_type_id = attachment.order_type_id,
                    created_at = attachment.created_at,
                    updated_at = timezone.now()
                )

            # #print(" OrderAttachments replicated to mstcnl")

            #  8) Copy Custom Fields
            custom_fields = CustomFieldValue.objects.using('default').filter(custom_id=sale_order_id)
            for cf in custom_fields:
                MstcnlCustomFieldValue.objects.using('mstcnl').create(
                    custom_field_value_id = cf.custom_field_value_id,
                    custom_field_id = cf.custom_field_id,
                    entity_id = cf.entity_id,
                    field_value = cf.field_value,
                    field_value_type = cf.field_value_type,
                    created_at = cf.created_at,
                    updated_at = timezone.now(),
                    custom_id = cf.custom_id
                )
                
            # # #print(" CustomFields replicated to mstcnl")
            
            time.sleep(1)
                
            SaleOrderItems.objects.using('default').filter(sale_order_id=sale_order_id).delete()
            OrderShipments.objects.using('default').filter(order_id=sale_order_id).delete()
            OrderAttachments.objects.using('default').filter(order_id=sale_order_id).delete()
            CustomFieldValue.objects.using('default').filter(custom_id=sale_order_id).delete()
            SaleOrder.objects.using('default').filter(pk=sale_order_id).delete()

            return {"message": f"SaleOrder {sale_order_id} replicated to mstcnl"}

    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e)}

#helper method
# views.py
from rest_framework.decorators import api_view

@api_view(['GET'])
def pending_sale_quantities(request):
    set_db('default')
    using_db = 'default'

    items = SaleOrderItems.objects.using(using_db).filter(
        production_qty__gt=0
    ).select_related('sale_order_id', 'product_id', 'sale_order_id__customer_id')

    data = {}
    for i in items:
        order = i.sale_order_id

        if order.sale_order_id not in data:
            data[order.sale_order_id] = {
                "sale_order_id": order.sale_order_id,
                "order_no": order.order_no,
                "order_date": order.order_date,
                "customer_name": order.customer_id.name if order.customer_id else '',
                "pending_items": []
            }

        data[order.sale_order_id]["pending_items"].append({
            "sale_order_item_id": i.sale_order_item_id,
            "product_id": i.product_id_id,
            "product_name": i.product_id.name if i.product_id else '',
            "production_qty": i.production_qty,
            "rate": i.rate,
            "tax": i.tax,
            "unit_options_id": i.unit_options_id_id if i.unit_options_id else None
        })

    return build_response(
        1,
        "Pending quantities fetched",
        list(data.values()),
        status.HTTP_200_OK
    )
    