from decimal import Decimal
import logging
import time
from django.http import Http404
from django.shortcuts import render, get_object_or_404
from rest_framework import viewsets
from apps.auditlogs.utils import log_user_action
from apps.customfields.models import CustomFieldValue
from apps.customfields.serializers import CustomFieldValueSerializer
from apps.finance.models import JournalEntryLines
from apps.finance.views import JournalEntryLinesAPIView
from apps.purchase.filters import BillPaymentTransactionsReportFilter, PurchaseInvoiceOrdersFilter, PurchaseOrdersFilter, PurchaseReturnOrdersFilter
from apps.purchase.filters import OutstandingPurchaseFilter, PurchaseInvoiceOrdersFilter, PurchaseOrderItemsFilter, PurchaseOrdersFilter, PurchaseReturnOrdersFilter, PurchasesByVendorReportFilter, PurchasesbyVendorReportFilter, StockReplenishmentReportFilter
from apps.vendor.views import VendorBalanceView
from config.utils_db_router import set_db
from config.utils_filter_methods import filter_response
from .models import *
from .serializers import *
from config.utils_methods import *
from config.utils_variables import *
from config.utils_methods import update_multi_instances, validate_input_pk, delete_multi_instance, generic_data_creation, get_object_or_none, list_all_objects, create_instance, update_instance, build_response, validate_multiple_data, validate_order_type, validate_payload_data, validate_put_method_data
from uuid import UUID
from apps.products.models import Products, ProductVariation
from apps.sales.serializers import OrderAttachmentsSerializer,OrderShipmentsSerializer
from apps.sales.models import OrderAttachments,OrderShipments
from rest_framework import viewsets
from apps.masters.models import OrderTypes
from rest_framework.views import APIView
from django.db import transaction
from rest_framework.serializers import ValidationError
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter
from django.db.models import Sum, F, Count, Min,Max,Avg, ExpressionWrapper, DecimalField,IntegerField
from django.db.models.functions import Coalesce


# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

# Create your views here.
class PurchaseOrdersViewSet(viewsets.ModelViewSet):
    queryset = PurchaseOrders.objects.all()
    serializer_class = PurchaseOrdersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PurchaseOrdersFilter
    ordering_fields = []
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class PurchaseorderItemsViewSet(viewsets.ModelViewSet):
    queryset = PurchaseorderItems.objects.all()
    serializer_class = PurchaseorderItemsSerializer
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class PurchaseInvoiceOrdersViewSet(viewsets.ModelViewSet):
    queryset = PurchaseInvoiceOrders.objects.all()
    serializer_class = PurchaseInvoiceOrdersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PurchaseInvoiceOrdersFilter
    ordering_fields = []
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class PurchaseInvoiceItemViewSet(viewsets.ModelViewSet):
    queryset = PurchaseInvoiceItem.objects.all()
    serializer_class = PurchaseInvoiceItemSerializer
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class PurchaseReturnOrdersViewSet(viewsets.ModelViewSet):
    queryset = PurchaseReturnOrders.objects.all()
    serializer_class = PurchaseReturnOrdersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PurchaseReturnOrdersFilter
    ordering_fields = []
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
   
class PurchaseReturnItemsViewSet(viewsets.ModelViewSet):
    queryset = PurchaseReturnItems.objects.all()
    serializer_class = PurchaseReturnItemsSerializer
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
 
class PurchasePriceListViewSet(viewsets.ModelViewSet):
    queryset = PurchasePriceList.objects.all()
    serializer_class = PurchasePriceListSerializer
 
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)
 
    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)
 
    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
#=======================PurchaseOrder=====================================================
class PurchaseOrderViewSet(APIView):
    """
    API ViewSet for handling purchase order creation and related data.
    """
    def get_object(self, pk):
        try:
            return PurchaseOrders.objects.get(pk=pk)
        except PurchaseOrders.DoesNotExist:
            logger.warning(f"PurchaseOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        
    def get(self, request, *args, **kwargs):
        """Handles GET requests with filters and reports."""
        try:
            if "pk" in kwargs:
                result = validate_input_pk(self, kwargs['pk'])
                return result if result else self.retrieve(self, request, *args, **kwargs)

            if request.query_params.get("summary", "false").lower() == "true":
                return self.get_summary_data(request)
            
            if request.query_params.get("purchases_by_vendor", "false").lower() == "true":
                return self.get_purchases_by_vendor_report(request)
            
            if request.query_params.get("outstanding_purchases", "false").lower() == "true":
                return self.get_outstanding_purchases(request)
            
            if request.query_params.get("landed_cost_report", "false").lower() == "true":
                return self.get_landed_cost_report(request)
            
            if request.query_params.get("purchase_price_variance_report", "false").lower() == "true":
                return self.get_purchase_price_variance_report(request)
            
            if request.query_params.get("stock_replenishment_report", "false").lower() == "true":
                return self.get_stock_replenishment_report(request)

            return self.get_purchase_orders(request)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_pagination_params(self, request):
        """Extracts pagination parameters from the request."""
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        return page, limit
    
    # def apply_filters(self, request, queryset, filter_class, model_class):
    #     """Generic function to apply filters on any queryset and return total count."""
    #     if request.query_params:
    #         filterset = filter_class(request.GET, queryset=queryset)
    #         if filterset.is_valid():
    #             queryset = filterset.qs  

    #     total_count = model_class.objects.count()  # Total count calculation
    #     return queryset, total_count
    
    def get_purchase_orders(self, request):
        """Fetches filtered purchase orders."""
        logger.info("Retrieving all purchase orders")
        page, limit = self.get_pagination_params(request)
        
        queryset = PurchaseOrders.objects.all().order_by('is_deleted', '-created_at')

        # Apply filters
        if request.query_params:
            filterset = PurchaseOrdersFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
                
        total_count = PurchaseOrders.objects.count()
        serializer = PurchaseOrdersSerializer(queryset, many=True)
        return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

    def get_summary_data(self, request):
        """Fetches purchase order summary data."""
        logger.info("Retrieving Purchase order summary")

        page, limit = self.get_pagination_params(request)
        queryset = PurchaseOrders.objects.all().order_by('is_deleted', '-created_at')

        # Apply filters
        if request.query_params:
            filterset = PurchaseOrdersFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
                
        total_count = PurchaseOrders.objects.count()
        serializer = PurchaseOrdersOptionsSerializer(queryset, many=True)
        return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)
    
    def get_purchases_by_vendor_report(self, request):
        """Fetches total purchases aggregated by vendor."""
        logger.info("Retrieving purchases by vendor report data")
        page, limit = self.get_pagination_params(request)
        
        # Group data by vendor (using vendor_id__name) and aggregate the total purchase amount and count of invoices.
        queryset = PurchaseInvoiceOrders.objects.values(
            vendor=F('vendor_id__name')
        ).annotate(
            total_purchase=Sum('total_amount', output_field=DecimalField(max_digits=18, decimal_places=2)),
            order_count=Count('purchase_invoice_id')
        ).order_by('-total_purchase')
        
        # Optional filtering using PurchasesByVendorReportFilter.
        if request.query_params:
            filterset = PurchasesByVendorReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = queryset.count()
        serializer = PurchasesByVendorReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
    
    def get_outstanding_purchases(self, request):
        """Fetches outstanding purchase payments to vendors."""
        logger.info("Retrieving outstanding purchase payments report")

        page, limit = self.get_pagination_params(request)

        queryset = PurchaseInvoiceOrders.objects.values(vendor_name=F('vendor_id__name'), invoice_num=F('invoice_no'), invoice_dates=F('invoice_date'), due_dates=F('due_date'),total_amounts=F('total_amount'),advance_payments=F('advance_amount')
         ).annotate(
            outstanding_amount=ExpressionWrapper(F('total_amount') - F('advance_amount'),output_field=DecimalField()),
            payment_status=ExpressionWrapper(F('total_amount') - F('advance_amount'),output_field=DecimalField())
        ).filter(outstanding_amount__gt=0).order_by('-due_date')

        # Apply filters
        filterset = OutstandingPurchaseFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs

        total_count = queryset.count()
        serializer = OutstandingPurchaseReportSerializer(queryset, many=True)
        return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)
    
    def get_landed_cost_report(self, request):
        """Fetches landed cost report total cost including taxes, shipping, etc."""
        logger.info("Retrieving Landed Cost Report...")
        page, limit = self.get_pagination_params(request)
        
        queryset = PurchaseInvoiceOrders.objects.select_related("vendor_id").annotate(
            vendor_name=F("vendor_id__name"),  #  Fetch vendor name correctly
            landed_cost=ExpressionWrapper(
                F("total_amount") + F("tax_amount") + F("cess_amount") +
                Coalesce(F("transport_charges"), 0) - Coalesce(F("dis_amt"), 0) +
                Coalesce(F("round_off"), 0),
                output_field=DecimalField()
            )
        ).order_by("-invoice_no")
        
         # Apply filters
        filterset = PurchaseInvoiceOrdersFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
            
        total_count = queryset.count()
        serializer = LandedCostReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
    

    def get_purchase_price_variance_report(self, request):
        """Fetches purchase price variance report – compare purchase prices over time."""
        logger.info(" Retrieving Purchase Price Variance Report...")

        page, limit = self.get_pagination_params(request)
        
        queryset = PurchaseorderItems.objects.select_related("product_id", "purchase_order_id__vendor_id").annotate(
            product=F("product_id__name"),
            vendor_name=F("purchase_order_id__vendor_id__name"),
            order_date=F("purchase_order_id__order_date"), 
            min_price=Min("rate"),
            max_price=Max("rate"),
            avg_price=Avg("rate")
        ).order_by("product_id__name", "purchase_order_id__order_date")


         # Apply filters
        filterset = PurchaseOrderItemsFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
            
        total_count = queryset.count()
        serializer = PurchasePriceVarianceReportSerializer(queryset, many=True)

        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    def get_stock_replenishment_report(self, request):
        """Fetches suggested purchases based on stock levels.
        Shows products that need to be reordered based on stock levels:"""
        logger.info("Retrieving stock replenishment report data")
        page, limit = self.get_pagination_params(request)
        
        # Filter for products where current stock (balance) is less than the minimum desired (minimum_level)
        queryset = Products.objects.filter(balance__lt=F('minimum_level')).annotate(
            reorder_quantity=ExpressionWrapper(F('minimum_level') - F('balance'), output_field=IntegerField()),
            current_stock=F('balance')  # Map balance to current_stock for consistency
        ).order_by('name')
        
        # Apply filters using StockReplenishmentReportFilter
        if request.query_params:
            filterset = StockReplenishmentReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
        
        total_count = queryset.count()
        serializer = StockReplenishmentReportSerializer(queryset, many=True)
        return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)
        
        

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a purchase order and its related data (items, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the PurchaseOrders instance
            purchase_order = get_object_or_404(PurchaseOrders, pk=pk)
            purchase_order_serializer = PurchaseOrdersSerializer(purchase_order)

            # Retrieve related data
            items_data = self.get_related_data(PurchaseorderItems, PurchaseorderItemsSerializer, 'purchase_order_id', pk)
            attachments_data = self.get_related_data(OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk)
            shipments_data = self.get_related_data(OrderShipments, OrderShipmentsSerializer, 'order_id', pk)
            shipments_data = shipments_data[0] if len(shipments_data)>0 else {}
             
            # Retrieve custom field values
            custom_field_values_data = self.get_related_data(CustomFieldValue, CustomFieldValueSerializer, 'custom_id', pk)
             
            # Customizing the response data
            custom_data = {
                "purchase_order_data": purchase_order_serializer.data,
                "purchase_order_items": items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data,
                "custom_field_values": custom_field_values_data
            }
            logger.info("Purchase order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        
        except Http404:
            logger.error("Purchase order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving purchase order with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.", model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s", model.__name__, filter_field, filter_value, str(e))
            return []

    # @transaction.atomic
    # def delete(self, request, pk, *args, **kwargs):
    #     """
    #     Handles the deletion of a purchase order and its related attachments and shipments.
    #     """
    #     try:
    #         # Get the PurchaseOrders instance
    #         instance = PurchaseOrders.objects.get(pk=pk)

    #         # Delete related OrderAttachments and OrderShipments
    #         if not delete_multi_instance(pk, PurchaseOrders, OrderAttachments, main_model_field_name='order_id'):
    #             return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         if not delete_multi_instance(pk, PurchaseOrders, OrderShipments, main_model_field_name='order_id'):
    #             return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         if not delete_multi_instance(pk, PurchaseOrders, CustomFieldValue, main_model_field_name='custom_id'):
    #             return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    #         # Delete the main PurchaseOrders instance
    #         instance.delete()

    #         logger.info(f"PurchaseOrders with ID {pk} deleted successfully.")
    #         return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
    #     except PurchaseOrders.DoesNotExist:
    #         logger.warning(f"PurchaseOrders with ID {pk} does not exist.")
    #         return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         logger.error(f"Error deleting PurchaseOrders with ID {pk}: {str(e)}")
    #         return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the soft deletion of a purchase order and its related attachments and shipments.
        """
        try:
            # Get the PurchaseOrders instance
            instance = PurchaseOrders.objects.get(pk=pk)

            # Soft delete related OrderAttachments, OrderShipments, CustomFieldValue
            if not delete_multi_instance(pk,PurchaseOrders, OrderAttachments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not delete_multi_instance(pk, PurchaseOrders, OrderShipments, main_model_field_name='order_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            if not delete_multi_instance(pk, PurchaseOrders, CustomFieldValue, main_model_field_name='custom_id'):
                return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Soft delete the main PurchaseOrders instance
            instance.is_deleted = True
            instance.save()

            logger.info(f"PurchaseOrders with ID {pk} soft-deleted successfully.")
            return build_response(1, "Record soft-deleted successfully", [], status.HTTP_204_NO_CONTENT)

        except PurchaseOrders.DoesNotExist:
            logger.warning(f"PurchaseOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error soft-deleting PurchaseOrders with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted PurchaseOrders record (is_deleted=True → is_deleted=False).
        """
        try:
            instance = PurchaseOrders.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"PurchaseOrders with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save()
            # Log the Create
            log_user_action(
                set_db('default'),
                request.user,
                "Patch",
                "Purchase Order",
                pk,
                f"{instance.order_no} - Purchase Order Restored by {request.user.username}"
            )

            logger.info(f"PurchaseOrders with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except PurchaseOrders.DoesNotExist:
            logger.warning(f"PurchaseOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring PurchaseOrders with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Extracting data from the request
        given_data = request.data

        #---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """

        # Validated PurchaseOrders Data
        purchase_order_data = given_data.pop('purchase_order_data', None) # parent_data
        if purchase_order_data:
            order_error = validate_payload_data(self, purchase_order_data , PurchaseOrdersSerializer)
            # validate the order_type in 'purchase_order' data
            validate_order_type(purchase_order_data, order_error, OrderTypes,look_up='order_type')


        # Validated PurchaseorderItems Data
        purchase_order_items_data = given_data.pop('purchase_order_items', None)
        
        # ---------------- CLEAN EMPTY Purchase ORDER ITEMS ---------------- #
        # Remove blank/empty payloads created by frontend (5 default rows)
        purchase_order_items_data = [
            item for item in purchase_order_items_data
            if item.get("product_id") and item.get("quantity")
        ]
        #----------------------------------------------------------

        
        if purchase_order_items_data:
            item_error = validate_multiple_data(self, purchase_order_items_data,PurchaseorderItemsSerializer,['purchase_order_id'])

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(self, order_attachments_data ,OrderAttachmentsSerializer,['order_id','order_type_id'])
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_multiple_data(self, [order_shipments_data] , OrderShipmentsSerializer,['order_id','order_type_id'])
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Validate Custom Fields Data
        custom_fields_data = given_data.pop('custom_field_values', None)
        if custom_fields_data:
            custom_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'])
        else:
            custom_error = []

        # Ensure mandatory data is present
        if not purchase_order_data or not purchase_order_items_data:
            logger.error("Purchase order & Purchase order items & CustomFields are mandatory but not provided.")
            return build_response(0, "Purchase order & Purchase order items & CustomFields  are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if order_error:
            errors["purchase_order_data"] = order_error
        if item_error:
                errors["purchase_order_items"] = item_error
        if attachment_error:
                errors['order_attachments'] = attachment_error
        if shipments_error:
                errors['order_shipments'] = shipments_error
        if custom_error:
            errors['custom_field_values'] = custom_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
        
        #---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """
            
        # Hence the data is validated , further it can be created.

        # Create PurchaseOrders Data
        new_purchase_order_data = generic_data_creation(self, [purchase_order_data], PurchaseOrdersSerializer)
        new_purchase_order_data = new_purchase_order_data[0]
        purchase_order_id = new_purchase_order_data.get("purchase_order_id",None) #Fetch purchase_order_id from mew instance
        logger.info('PurchaseOrders - created*')

        # Create PurchaseorderItems Data
        update_fields = {'purchase_order_id':purchase_order_id}
        items_data = generic_data_creation(self, purchase_order_items_data, PurchaseorderItemsSerializer, update_fields)
        logger.info('PurchaseorderItems - created*')

        # Get order_type_id from OrderTypes model
        order_type_val = purchase_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id':purchase_order_id, 'order_type_id':type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(self, order_attachments_data, OrderAttachmentsSerializer, update_fields)
            logger.info('OrderAttchments - created*')
        else:
            # Since OrderAttchments Data is optional, so making it as an empty data list
            order_attachments = []

        # create OrderShipments Data
        if order_shipments_data:
            order_shipments = generic_data_creation(self, [order_shipments_data], OrderShipmentsSerializer, update_fields)
            order_shipments = order_shipments[0]
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = {}
            
        # Assign `custom_id = vendor_id` for CustomFieldValues
        if custom_fields_data:
            update_fields = {'custom_id': purchase_order_id}  # Now using `custom_id` like `order_id`
            custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, update_fields)
            logger.info('CustomFieldValues - created*')
        else:
            custom_fields_data = []

        custom_data = {
            "purchase_order":new_purchase_order_data,
            "purchase_order_items":items_data,
            "order_attachments":order_attachments,
            "order_shipments":order_shipments,
            "custom_field_values": custom_fields_data
        }
        
        orderno = purchase_order_data.get("order_no")
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "CREATE",
            "Purchase Order",
            purchase_order_id,
            f"{orderno} - Purchase Order Record Created by {request.user.username}"
        )

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
   
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        #----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Validated PurchaseOrders Data
        purchase_order_data = given_data.pop('purchase_order_data', None) # parent_data
        if purchase_order_data:
            purchase_order_data['purchase_order_id'] = pk    
            order_error = validate_multiple_data(self, purchase_order_data , PurchaseOrdersSerializer,['order_no'])
            # validate the 'order_type' in 'purchase_order_data' data
            validate_order_type(purchase_order_data, order_error, OrderTypes,look_up='order_type')

        # Validated PurchaseorderItems Data
        purchase_order_items_data = given_data.pop('purchase_order_items', None)
        
        # Filter out empty UI rows (only keep rows with real product)
        if purchase_order_items_data:
            purchase_order_items_data = [
                item for item in purchase_order_items_data
                if item.get("product_id") and item.get("quantity")
            ]
        
        if purchase_order_items_data:
            exclude_fields = ['purchase_order_id']
            item_error = validate_put_method_data(self, purchase_order_items_data, PurchaseorderItemsSerializer, exclude_fields, PurchaseorderItems, current_model_pk_field='purchase_order_item_id')

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id','order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, [order_shipments_data], OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Validated CustomFieldValues Data
        custom_field_values_data = given_data.pop('custom_field_values', None)
        if custom_field_values_data:
            exclude_fields = ['custom_id']
            custom_field_values_error = validate_put_method_data(self, custom_field_values_data, CustomFieldValueSerializer, exclude_fields, CustomFieldValue, current_model_pk_field='custom_field_value_id')
        else:
            custom_field_values_error = []

        # Ensure mandatory data is present
        if not purchase_order_data or not purchase_order_items_data:
            logger.error("Purchase order and Purchase order items & CustomFields are mandatory but not provided.")
            return build_response(0, "Purchase order and Purchase order items & CustomFields are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if order_error:
            errors["purchase_order_data"] = order_error
        if item_error:
            errors["purchase_order_items"] = item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if custom_field_values_error:
            errors['custom_field_values'] = custom_field_values_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        # update PurchaseOrders
        if purchase_order_data:
            update_fields = {} # No need to update any fields
            purchaseorder_data = update_multi_instances(self, pk, [purchase_order_data], PurchaseOrders, PurchaseOrdersSerializer, update_fields,main_model_related_field='purchase_order_id', current_model_pk_field='purchase_order_id')
            purchaseorder_data = purchaseorder_data[0] if len(purchaseorder_data)==1 else purchaseorder_data

        # Update the 'purchase_order_items'
        update_fields = {'purchase_order_id':pk}
        items_data = update_multi_instances(self, pk, purchase_order_items_data, PurchaseorderItems, PurchaseorderItemsSerializer, update_fields, main_model_related_field='purchase_order_id', current_model_pk_field='purchase_order_item_id')

        # Get 'order_type_id' from 'OrderTypes' model
        order_type_val = purchase_order_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id':pk, 'order_type_id':type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id')

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id')
        shipment_data = shipment_data[0] if len(shipment_data)==1 else shipment_data

        # Update CustomFieldValues Data
        if custom_field_values_data:
            custom_field_values_data = update_multi_instances(self, pk, custom_field_values_data, CustomFieldValue, CustomFieldValueSerializer, {}, main_model_related_field='custom_id', current_model_pk_field='custom_field_value_id')
            
        custom_data = {
            "purchase_order":purchaseorder_data,
            "purchase_order_items":items_data if items_data else [],
            "order_attachments":attachment_data if attachment_data else [],
            "order_shipments":shipment_data if shipment_data else {},
            "custom_field_values": custom_field_values_data if custom_field_values_data else []  # Add custom field values to response
        }
        orderno = purchase_order_data.get("order_no")
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "UPDATE",
            "Purchase Order",
            pk,
            f"{orderno} - Purchase Order Record Updated by {request.user.username}"
        )

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
    
#=======================PurchaseInvoiceOrder==============================================

class PurchaseInvoiceOrderViewSet(APIView):
    """
    API ViewSet for handling Purchase Invoice Order creation and related data.
    """
    def get_object(self, pk):
        try:
            return PurchaseInvoiceOrders.objects.get(pk=pk)
        except PurchaseInvoiceOrders.DoesNotExist:
            logger.warning(f"PurchaseInvoiceOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)   
      
    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
           result =  validate_input_pk(self,kwargs['pk'])
           return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            summary = request.query_params.get("summary", "false").lower() == "true"+ "&"
            if summary:
                logger.info("Retrieving Purchase Invoice orders summary")
                purchaseinvoiceorders = PurchaseInvoiceOrders.objects.all().order_by('is_deleted', '-created_at')
                data = PurchaseInvoiceOrdersOptionsSerializer.get_purchase_invoice_orders_summary(purchaseinvoiceorders)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
            
            instance = PurchaseInvoiceOrders.objects.all()

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = PurchaseInvoiceOrders.objects.count()

            # Apply filters manually
            if request.query_params:
                queryset = PurchaseInvoiceOrders.objects.all().order_by('is_deleted', '-created_at')
                filterset = PurchaseInvoiceOrdersFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
                    serializer = PurchaseInvoiceOrdersOptionsSerializer(queryset, many=True)
                    # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
                    return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except PurchaseInvoiceOrders.DoesNotExist:
            logger.error("Purchase invoice order does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        else:
            serializer = PurchaseInvoiceOrdersSerializer(instance, many=True)
            logger.info("Purchase invoice order data retrieved successfully.")
            return build_response(instance.count(), "Success", serializer.data, status.HTTP_200_OK)      
     
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a Purchase Invoice Orders and its related data (Invoiceitems, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the PurchaseInvoiceOrders instance
            purchase_invoice_order = get_object_or_404(PurchaseInvoiceOrders, pk=pk)
            purchase_invoice_order_serializer = PurchaseInvoiceOrdersSerializer(purchase_invoice_order)

            # Retrieve related data
            invoice_items_data = self.get_related_data(PurchaseInvoiceItem, PurchaseInvoiceItemSerializer, 'purchase_invoice_id', pk)
            attachments_data = self.get_related_data(OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk)
            shipments_data = self.get_related_data(OrderShipments, OrderShipmentsSerializer, 'order_id', pk)
            shipments_data = shipments_data[0] if len(shipments_data)>0 else {}
               
            # Retrieve custom field values
            custom_field_values_data = self.get_related_data(CustomFieldValue, CustomFieldValueSerializer, 'custom_id', pk)
             
            # Customizing the response data
            custom_data = {
                "purchase_invoice_orders": purchase_invoice_order_serializer.data,
                "purchase_invoice_items": invoice_items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data,
                "custom_field_values": custom_field_values_data
            }
            logger.info("Purchase invoice Order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        
        except Http404:
            logger.error("Purchase invoice order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving purchase invoice order with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
      
    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.", model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s", model.__name__, filter_field, filter_value, str(e))
            return []

    # @transaction.atomic
    # def delete(self, request, pk, *args, **kwargs):
    #     """
    #     Soft delete PurchaseInvoiceOrders and its related models using shared delete_multi_instance utility.
    #     """
    #     try:
    #         # Get the PurchaseInvoiceOrders instance
    #         instance = PurchaseInvoiceOrders.objects.get(pk=pk, is_deleted=False)
    #         instance.is_deleted = True
    #         instance.save()

    #         # Soft delete related OrderAttachments
    #         if not delete_multi_instance(pk, PurchaseInvoiceOrders, OrderAttachments, main_model_field_name='order_id'):
    #             return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    #         # Soft delete related OrderShipments
    #         if not delete_multi_instance(pk, PurchaseInvoiceOrders, OrderShipments, main_model_field_name='order_id'):
    #             return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    #         # Soft delete related CustomFieldValue
    #         if not delete_multi_instance(pk, PurchaseInvoiceOrders, CustomFieldValue, main_model_field_name='custom_id'):
    #             return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    #         logger.info(f"PurchaseInvoiceOrders with ID {pk} soft-deleted successfully.")
    #         return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)

    #     except PurchaseInvoiceOrders.DoesNotExist:
    #         logger.warning(f"PurchaseInvoiceOrders with ID {pk} does not exist or is already deleted.")
    #         return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    #     except Exception as e:
    #         logger.error(f"Error deleting PurchaseInvoiceOrders with ID {pk}: {str(e)}")
    #         return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the cancellation of a purchase invoice:
        - Marks it as 'Cancelled' instead of deleting
        - Reverts products back to inventory
        - Creates reversing ledger entry
        """
        try:
            # Get the PurchaseInvoiceOrders instance
            instance = PurchaseInvoiceOrders.objects.get(pk=pk)

            # Get the "Cancelled" status
            try:
                canceled_status = OrderStatuses.objects.get(status_name='Cancelled')
            except OrderStatuses.DoesNotExist:
                logger.error("'Cancelled' status not found in OrderStatuses table")
                return build_response(0, "Cannot cancel invoice - required status not found", [], status.HTTP_400_BAD_REQUEST)

            # --- STEP 1: Update invoice status to "Cancelled"
            instance.order_status_id = canceled_status
            instance.save()
            invoice_no = instance.invoice_no
            supplier_id = instance.vendor_id

            # --- STEP 2: Revert products back to inventory
            try:
                invoice_items = PurchaseInvoiceItem.objects.filter(purchase_invoice_id=instance.purchase_invoice_id)

                for item in invoice_items:
                    product = item.product_id  # ForeignKey to Product
                    product.balance = F('balance') + item.quantity
                    product.save()

                logger.info(f"Reverted {len(invoice_items)} products to inventory for cancelled purchase invoice {invoice_no}")

            except Exception as e:
                logger.error(f"Error reverting products to inventory for purchase invoice {invoice_no}: {str(e)}")

            # --- STEP 3: Create offsetting ledger entry
            existing_balance = (
                JournalEntryLines.objects.filter(vendor_id=supplier_id)
                .order_by('is_deleted', '-created_at')
                .values_list('balance', flat=True)
                .first()
            ) or Decimal('0.00')

            latest_balance = existing_balance - Decimal(instance.total_amount)

            try:
                JournalEntryLines.objects.create(
                    description=f"Cancellation of purchase invoice {invoice_no}",
                    debit=instance.total_amount,
                    credit=0,
                    voucher_no=invoice_no,
                    vendor_id=supplier_id,
                    balance=latest_balance
                )
                logger.info(f"Created offsetting debit entry of {instance.total_amount} for cancelled purchase invoice {invoice_no}")
            except Exception as e:
                logger.error(f"Error creating offsetting debit entry: {str(e)}")

            # --- STEP 4: Return success response
            return build_response(1, "Purchase invoice cancelled successfully", [], status.HTTP_200_OK)

        except PurchaseInvoiceOrders.DoesNotExist:
            logger.warning(f"PurchaseInvoiceOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error cancelling PurchaseInvoiceOrders with ID {pk}: {str(e)}")
            return build_response(0, "Purchase invoice cancellation failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    # @transaction.atomic
    # def delete(self, request, pk, *args, **kwargs):
    #     """
    #     Handles the deletion of a Purchase Invoice Orders and its related attachments and shipments.
    #     """
    #     try:
    #         # Get the PurchaseInvoiceOrders instance
    #         instance = PurchaseInvoiceOrders.objects.get(pk=pk)

    #         # Delete related OrderAttachments and OrderShipments
    #         if not delete_multi_instance(pk, PurchaseInvoiceOrders, OrderAttachments, main_model_field_name='order_id'):
    #             return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         if not delete_multi_instance(pk, PurchaseInvoiceOrders, OrderShipments, main_model_field_name='order_id'):
    #             return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         if not delete_multi_instance(pk, PurchaseInvoiceOrders, CustomFieldValue, main_model_field_name='custom_id'):
    #             return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         # Delete the main PurchaseInvoiceOrders instance
    #         instance.delete()

    #         logger.info(f"PurchaseInvoiceOrders with ID {pk} deleted successfully.")
    #         return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
    #     except PurchaseInvoiceOrders.DoesNotExist:
    #         logger.warning(f"PurchaseInvoiceOrders with ID {pk} does not exist.")
    #         return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         logger.error(f"Error deleting PurchaseInvoiceOrders with ID {pk}: {str(e)}")
    #         return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted PurchaseInvoiceOrders record (is_deleted=True → is_deleted=False).
        """
        try:
            instance = PurchaseInvoiceOrders.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"PurchaseInvoiceOrders with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save()

            logger.info(f"PurchaseInvoiceOrders with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except PurchaseInvoiceOrders.DoesNotExist:
            logger.warning(f"PurchaseInvoiceOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring PurchaseInvoiceOrders with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Extracting data from the request
        given_data = request.data

        #---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
 
        """

        # Validated PurchaseInvoiceOrders Data
        purchase_invoice_orders_data = given_data.pop('purchase_invoice_orders', None) # parent_data
        if purchase_invoice_orders_data:
            invoice_order_error = validate_payload_data(self, purchase_invoice_orders_data , PurchaseInvoiceOrdersSerializer)
            # validate the order_type in 'PurchaseInvoiceOrders' data
            validate_order_type(purchase_invoice_orders_data, invoice_order_error, OrderTypes,look_up='order_type')
                
        # Validated PurchaseInvoiceItems Data
        purchase_invoice_items_data = given_data.pop('purchase_invoice_items', None)
        
        purchase_invoice_items_data = [
            item for item in purchase_invoice_items_data
            if item.get("product_id") and item.get("quantity")
        ]
        
        if purchase_invoice_items_data:
            invoice_item_error = validate_multiple_data(self, purchase_invoice_items_data,PurchaseInvoiceItemSerializer,['purchase_invoice_id'])

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(self, order_attachments_data ,OrderAttachmentsSerializer,['order_id','order_type_id'])
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_multiple_data(self, [order_shipments_data] , OrderShipmentsSerializer,['order_id','order_type_id'])
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Validate Custom Fields Data
        custom_fields_data = given_data.pop('custom_field_values', None)
        if custom_fields_data:
            custom_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'])
        else:
            custom_error = []

        # Ensure mandatory data is present
        if not purchase_invoice_orders_data or not purchase_invoice_items_data:
            logger.error("Purchase invoice order and Purchase invoice items & CustomFields are mandatory but not provided.")
            return build_response(0, "Purchase invoice order and Purchase invoice items & & CustomFields are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if invoice_order_error:
            errors["purchase_invoice_orders"] = invoice_order_error
        if invoice_item_error:
                errors["purchase_invoice_items"] = invoice_item_error
        if attachment_error:
                errors['order_attachments'] = attachment_error
        if shipments_error:
                errors['order_shipments'] = shipments_error
        if custom_error:
            errors['custom_field_values'] = custom_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
        
        # Stock verification
        stock_error = product_stock_verification(Products, ProductVariation, purchase_invoice_items_data)
        if stock_error:
            return build_response(0, f"ValidationError :", stock_error, status.HTTP_400_BAD_REQUEST)        
        
        #---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """
            
        # Hence the data is validated , further it can be created.

        # Create PurchaseInvoiceOrders Data
        new_purchase_invoice_orders_data = generic_data_creation(self, [purchase_invoice_orders_data], PurchaseInvoiceOrdersSerializer)
        new_purchase_invoice_orders_data = new_purchase_invoice_orders_data[0]
        purchase_invoice_id = new_purchase_invoice_orders_data.get("purchase_invoice_id",None) #Fetch purchase_invoice_id from mew instance
        logger.info('PurchaseInvoiceOrders - created*')

        # Create PurchaseInvoiceItem Data
        update_fields = {'purchase_invoice_id': purchase_invoice_id}
        invoice_items_data = generic_data_creation(self, purchase_invoice_items_data, PurchaseInvoiceItemSerializer, update_fields)
        logger.info('PurchaseInvoiceItem - created*')

        # Get order_type_id from OrderTypes model
        order_type_val = purchase_invoice_orders_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id':purchase_invoice_id, 'order_type_id':type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(self, order_attachments_data, OrderAttachmentsSerializer, update_fields)
            logger.info('OrderAttchments - created*')
        else:
            # Since OrderAttchments Data is optional, so making it as an empty data list
            order_attachments = []

        # create OrderShipments Data
        if order_shipments_data:
            order_shipments = generic_data_creation(self, [order_shipments_data], OrderShipmentsSerializer, update_fields)
            order_shipments = order_shipments[0]
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = {}
            
        # Assign `custom_id = purchase_invoice_id` for CustomFieldValues
        if custom_fields_data:
            update_fields = {'custom_id': purchase_invoice_id}  # Now using `custom_id` like `order_id`
            custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, update_fields)
            logger.info('CustomFieldValues - created*')
        else:
            custom_fields_data = []

        custom_data = {
            "purchase_invoice_orders":new_purchase_invoice_orders_data,
            "purchase_invoice_items":invoice_items_data,
            "order_attachments":order_attachments,
            "order_shipments":order_shipments,
            "custom_field_values": custom_fields_data
        }
        invoiceno = purchase_invoice_orders_data.get("invoice_no")
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "CREATE",
            "Purchase Invoice",
            purchase_invoice_id,
            f"{invoiceno} - Purchase Invoice Order Record Created by {request.user.username}"
        )

        # Update Product Stock
        update_product_stock(Products, ProductVariation, purchase_invoice_items_data, 'subtract')        

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        #----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Validated PurchaseInvoiceOrders Data
        purchase_invoice_orders_data = given_data.pop('purchase_invoice_orders', None) # parent_data
        if purchase_invoice_orders_data:
            purchase_invoice_orders_data['purchase_invoice_id'] = pk
            invoice_order_error = validate_multiple_data(self, purchase_invoice_orders_data , PurchaseInvoiceOrdersSerializer,['invoice_no'])
            # validate the 'order_type' in 'purchase_invoice_orders' data
            validate_order_type(purchase_invoice_orders_data, invoice_order_error, OrderTypes,look_up='order_type')

        # Validated PurchaseInvoiceItem Data
        purchase_invoice_items_data = given_data.pop('purchase_invoice_items', None)
        
        if purchase_invoice_items_data:
            purchase_invoice_items_data = [
                item for item in purchase_invoice_items_data
                if item.get("product_id") and item.get("quantity")
            ]
        
        if purchase_invoice_items_data:
            exclude_fields = ['purchase_invoice_id']
            invoice_item_error = validate_put_method_data(self, purchase_invoice_items_data, PurchaseInvoiceItemSerializer, exclude_fields, PurchaseInvoiceItem, current_model_pk_field='purchase_invoice_item_id')

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id','order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Validated CustomFieldValues Data
        custom_field_values_data = given_data.pop('custom_field_values', None)
        if custom_field_values_data:
            exclude_fields = ['custom_id']
            custom_field_values_error = validate_put_method_data(self, custom_field_values_data, CustomFieldValueSerializer, exclude_fields, CustomFieldValue, current_model_pk_field='custom_field_value_id')
        else:
            custom_field_values_error = []

        # Ensure mandatory data is present
        if not purchase_invoice_orders_data or not purchase_invoice_items_data:
            logger.error("Purchase invoice order and Purchase invoice items & CustomFields are mandatory but not provided.")
            return build_response(0, "Purchase invoice order and Purchase invoice items & CustomFields are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if invoice_order_error:
            errors["purchase_invoice_orders"] = invoice_order_error
        if invoice_item_error:
            errors["purchase_invoice_items"] = invoice_item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if custom_field_values_error:
            errors['custom_field_values'] = custom_field_values_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)        
      
        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        # update PurchaseInvoiceOrders
        if purchase_invoice_orders_data:
            update_fields = [] # No need to update any fields
            purchaseinvoiceorder_data = update_multi_instances(self, pk, purchase_invoice_orders_data, PurchaseInvoiceOrders, PurchaseInvoiceOrdersSerializer, update_fields,main_model_related_field='purchase_invoice_id', current_model_pk_field='purchase_invoice_id')
            purchaseinvoiceorder_data = purchaseinvoiceorder_data[0] if len(purchaseinvoiceorder_data)==1 else purchaseinvoiceorder_data

        # Update the 'PurchaseInvoiceItem'
        update_fields = {'purchase_invoice_id':pk}
        invoice_items_data = update_multi_instances(self, pk, purchase_invoice_items_data, PurchaseInvoiceItem, PurchaseInvoiceItemSerializer, update_fields, main_model_related_field='purchase_invoice_id', current_model_pk_field='purchase_invoice_item_id')

        # Get 'order_type_id' from 'OrderTypes' model
        order_type_val = purchase_invoice_orders_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id':pk, 'order_type_id':type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id')

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id')
        shipment_data = shipment_data[0] if len(shipment_data)==1 else shipment_data

        # Update CustomFieldValues Data
        if custom_field_values_data:
            custom_field_values_data = update_multi_instances(self, pk, custom_field_values_data, CustomFieldValue, CustomFieldValueSerializer, {}, main_model_related_field='custom_id', current_model_pk_field='custom_field_value_id')

        custom_data = {
            "purchase_invoice_orders":purchaseinvoiceorder_data,
            "purchase_invoice_items":invoice_items_data if invoice_items_data else [],
            "order_attachments":attachment_data if attachment_data else [],
            "order_shipments":shipment_data if shipment_data else {},
            "custom_field_values": custom_field_values_data if custom_field_values_data else []  # Add custom field values to response
        }
        invoiceno = purchase_invoice_orders_data.get("invoice_no")
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "UPDATE",
            "Purchase Invoice",
            pk,
            f"{invoiceno} - Purchase Invoice Order Record Updated by {request.user.username}"
        )

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

#=====================PurchaseReturnOrders========================================================
class PurchaseReturnOrderViewSet(APIView):
    """
    API ViewSet for handling Purchase Return Order creation and related data.
    """
    def get_object(self, pk):
        try:
            return PurchaseReturnOrders.objects.get(pk=pk)
        except PurchaseReturnOrders.DoesNotExist:
            logger.warning(f"PurchaseReturnOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)   
      
    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
           result =  validate_input_pk(self,kwargs['pk'])
           return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            summary = request.query_params.get("summary", "false").lower() == "true"+ "&"
            if summary:
                logger.info("Retrieving Purchase return orders summary")
                purchasereturnorders = PurchaseReturnOrders.objects.all().order_by('is_deleted', '-created_at')
                data = PurchaseReturnOrdersOptionsSerializer.get_purchase_return_orders_summary(purchasereturnorders)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
            
            instance = PurchaseReturnOrders.objects.all()
            
            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = PurchaseReturnOrders.objects.count()            
            
            # Apply filters manually
            if request.query_params:
                queryset = PurchaseReturnOrders.objects.all().order_by('is_deleted', '-created_at')
                filterset = PurchaseReturnOrdersFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
                    serializer = PurchaseReturnOrdersOptionsSerializer(queryset, many=True)
                    # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
                    return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except PurchaseReturnOrders.DoesNotExist:
            logger.error("Purchase return order does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        else:
            serializer = PurchaseReturnOrdersSerializer(instance, many=True)
            logger.info("Purchase return order data retrieved successfully.")
            return build_response(instance.count(), "Success", serializer.data, status.HTTP_200_OK)  
        
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a Purchase Return Orders and its related data (ReturnItems, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the PurchaseReturnOrders instance
            purchase_return_order = get_object_or_404(PurchaseReturnOrders, pk=pk)
            purchase_return_order_serializer = PurchaseReturnOrdersSerializer(purchase_return_order)

            # Retrieve related data
            return_items_data = self.get_related_data(PurchaseReturnItems, PurchaseReturnItemsSerializer, 'purchase_return_id', pk)
            attachments_data = self.get_related_data(OrderAttachments, OrderAttachmentsSerializer, 'order_id', pk)
            shipments_data = self.get_related_data(OrderShipments, OrderShipmentsSerializer, 'order_id', pk)
            shipments_data = shipments_data[0] if len(shipments_data)>0 else {}
                
            # Retrieve custom field values
            custom_field_values_data = self.get_related_data(CustomFieldValue, CustomFieldValueSerializer, 'custom_id', pk)
                
            # Customizing the response data
            custom_data = {
                "purchase_return_orders": purchase_return_order_serializer.data,
                "purchase_return_items": return_items_data,
                "order_attachments": attachments_data,
                "order_shipments": shipments_data,
                "custom_field_values": custom_field_values_data
            }
            logger.info("Purchase return Order and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        
        except Http404:
            logger.error("Purchase return order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving purchase return order with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
 
    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug("Retrieved related data for model %s with filter %s=%s.", model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s", model.__name__, filter_field, filter_value, str(e))
            return []
        
    # @transaction.atomic
    # def delete(self, request, pk, *args, **kwargs):
    #     """
    #     Handles the deletion of a Purchase Return Orders and its related attachments and shipments.
    #     """
    #     try:
    #         # Get the PurchaseReturnOrders instance
    #         instance = PurchaseReturnOrders.objects.get(pk=pk)

    #         # Delete related OrderAttachments and OrderShipments
    #         if not delete_multi_instance(pk, PurchaseReturnOrders, OrderAttachments, main_model_field_name='order_id'):
    #             return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         if not delete_multi_instance(pk, PurchaseReturnOrders, OrderShipments, main_model_field_name='order_id'):
    #             return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         if not delete_multi_instance(pk, PurchaseReturnOrders, CustomFieldValue, main_model_field_name='custom_id'):
    #             return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         # Delete the main PurchaseReturnOrders instance
    #         instance.is_deleted=True
    #         instance.save()

    #         logger.info(f"PurchaseReturnOrders with ID {pk} deleted successfully.")
    #         return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
    #     except PurchaseReturnOrders.DoesNotExist:
    #         logger.warning(f"PurchaseReturnOrders with ID {pk} does not exist.")
    #         return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         logger.error(f"Error deleting PurchaseReturnOrders with ID {pk}: {str(e)}")
    #         return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Cancels a Purchase Return:
        - Marks it as 'Cancelled'
        - If Damaged: skip inventory & ledger
        - If Wrong Product: revert inventory + ledger reversal (debit vendor)
        """
        try:
            instance = PurchaseReturnOrders.objects.get(pk=pk)

            # Get 'Cancelled' status
            try:
                canceled_status = OrderStatuses.objects.get(status_name='Cancelled')
            except OrderStatuses.DoesNotExist:
                logger.error("'Cancelled' status not found")
                return build_response(0, "Cannot cancel purchase return - required status not found", [], status.HTTP_400_BAD_REQUEST)

            # Update status
            instance.order_status_id = canceled_status
            instance.save()

            return_reason = getattr(instance, 'return_reason', None)
            return_no = getattr(instance, 'return_no', None)
            vendor_id = instance.vendor_id

            logger.info(f"Purchase Return {return_no} marked as Cancelled (Reason: {return_reason})")

            if return_reason and return_reason.lower() == 'damaged':
                logger.info(f"Skipping inventory & ledger for damaged return {return_no}")

            elif return_reason and return_reason.lower() == 'wrong product':
                # Revert inventory
                try:
                    return_items = PurchaseReturnItems.objects.filter(purchase_return_id=instance.purchase_return_id)
                    for item in return_items:
                        product = item.product_id
                        product.balance = F('balance') + item.quantity
                        product.save()
                    logger.info(f"Reverted {len(return_items)} products for return {return_no}")
                    # Log the Create
                    log_user_action(
                        set_db('default'),
                        request.user,
                        "RETURN",
                        "Purchase Return",
                        pk,
                        f"{instance.return_no} - products Reverted for return by {request.user.username}"
                    )
                except Exception as e:
                    logger.error(f"Error reverting products: {str(e)}")

                # Ledger reversal (debit vendor)
                try:
                    existing_balance = (
                        JournalEntryLines.objects.filter(vendor_id=vendor_id)
                        .order_by('is_deleted', '-created_at')
                        .values_list('balance', flat=True)
                        .first()
                    ) or Decimal('0.00')

                    latest_balance = existing_balance - Decimal(instance.total_amount)

                    JournalEntryLines.objects.create(
                        description=f"Cancellation of purchase return {return_no}",
                        debit=instance.total_amount,
                        credit=0,
                        voucher_no=return_no,
                        vendor_id=vendor_id,
                        balance=latest_balance
                    )
                    logger.info(f"Created reversal ledger entry for return {return_no}")
                    
                except Exception as e:
                    logger.error(f"Error creating ledger entry: {str(e)}")

            else:
                logger.warning(f"Unknown return reason for {return_no}, no additional action")

            return build_response(1, "Purchase return cancelled successfully", [], status.HTTP_200_OK)

        except PurchaseReturnOrders.DoesNotExist:
            logger.warning(f"Return ID {pk} not found")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error cancelling return {pk}: {str(e)}")
            return build_response(0, "Purchase return cancellation failed", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted PurchaseReturnOrders record (is_deleted=True → is_deleted=False).
        """
        try:
            instance = PurchaseReturnOrders.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"PurchaseReturnOrders with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save()

            logger.info(f"PurchaseReturnOrders with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except PurchaseReturnOrders.DoesNotExist:
            logger.warning(f"PurchaseReturnOrders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring PurchaseReturnOrders with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        

    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Extracting data from the request
        given_data = request.data

        #---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
 
        """

        # Validated PurchaseReturnOrders Data
        purchase_return_orders_data = given_data.pop('purchase_return_orders', None) # parent_data
        if purchase_return_orders_data:
            return_order_error = validate_payload_data(self, purchase_return_orders_data , PurchaseReturnOrdersSerializer)
            # validate the order_type in 'PurchaseReturnOrders' data
            validate_order_type(purchase_return_orders_data, return_order_error, OrderTypes,look_up='order_type')
                
        # Validated PurchaseInvoiceItems Data
        purchase_return_items_data = given_data.pop('purchase_return_items', None)
        
        purchase_return_items_data = [
            item for item in purchase_return_items_data
            if item.get("product_id") and item.get("quantity")
        ]
        
        if purchase_return_items_data:
            return_item_error = validate_multiple_data(self, purchase_return_items_data,PurchaseReturnItemsSerializer,['purchase_return_id'])

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        if order_attachments_data:
            attachment_error = validate_multiple_data(self, order_attachments_data ,OrderAttachmentsSerializer,['order_id','order_type_id'])
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_multiple_data(self, [order_shipments_data] , OrderShipmentsSerializer,['order_id','order_type_id'])
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Validate Custom Fields Data
        custom_fields_data = given_data.pop('custom_field_values', None)
        if custom_fields_data:
            custom_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'])
        else:
            custom_error = []

        # Ensure mandatory data is present
        if not purchase_return_orders_data or not purchase_return_items_data:
            logger.error("Purchase return order and Purchase return items & CustomFields are mandatory but not provided.")
            return build_response(0, "Purchase return order and Purchase return items & CustomFields are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if return_order_error:
            errors["purchase_return_orders"] = return_order_error
        if return_item_error:
                errors["purchase_return_items"] = return_item_error
        if attachment_error:
                errors['order_attachments'] = attachment_error
        if shipments_error:
                errors['order_shipments'] = shipments_error
        if custom_error:
            errors['custom_field_values'] = custom_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
        
        """
        Verifies if PREVIOUS PRODUCT INTANCE is available for the product.
        Raises a ValidationError if the product's instance is not present in database.
        """
        stock_error = previous_product_instance_verification(ProductVariation, purchase_return_items_data)
        if stock_error:
            return build_response(0, f"ValidationError :", stock_error, status.HTTP_400_BAD_REQUEST)        

        #---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """
            
        # Hence the data is validated , further it can be created.

        # Create PurchaseReturnOrders Data
        new_purchase_return_orders_data = generic_data_creation(self, [purchase_return_orders_data], PurchaseReturnOrdersSerializer)
        new_purchase_return_orders_data = new_purchase_return_orders_data[0]
        purchase_return_id = new_purchase_return_orders_data.get("purchase_return_id",None) #Fetch purchase_return_id from mew instance
        logger.info('PurchaseReturnOrders - created*')

        # Create PurchaseReturnItems Data
        update_fields = {'purchase_return_id': purchase_return_id}
        return_items_data = generic_data_creation(self, purchase_return_items_data, PurchaseReturnItemsSerializer, update_fields)
        logger.info('PurchaseReturnItems - created*')

        # Get order_type_id from OrderTypes model
        order_type_val = purchase_return_orders_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Create OrderAttchments Data
        update_fields = {'order_id':purchase_return_id, 'order_type_id':type_id}
        if order_attachments_data:
            order_attachments = generic_data_creation(self, order_attachments_data, OrderAttachmentsSerializer, update_fields)
            logger.info('OrderAttchments - created*')
        else:
            # Since OrderAttchments Data is optional, so making it as an empty data list
            order_attachments = []

        # create OrderShipments Data
        if order_shipments_data:
            order_shipments = generic_data_creation(self, [order_shipments_data], OrderShipmentsSerializer, update_fields)
            order_shipments = order_shipments[0]
            logger.info('OrderShipments - created*')
        else:
            # Since OrderShipments Data is optional, so making it as an empty data list
            order_shipments = {}
            
        # Assign `custom_id = purchase_return_id` for CustomFieldValues
        if custom_fields_data:
            update_fields = {'custom_id': purchase_return_id}  # Now using `custom_id` like `order_id`
            custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, update_fields)
            logger.info('CustomFieldValues - created*')
        else:
            custom_fields_data = []

        custom_data = {
            "purchase_return_orders":new_purchase_return_orders_data,
            "purchase_return_items":return_items_data,
            "order_attachments":order_attachments,
            "order_shipments":order_shipments,
            "custom_field_values": custom_fields_data
        }
        
        returnno = purchase_return_orders_data.get("return_no")
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "CREATE",
            "Purchase Return",
            purchase_return_id,
            f"{returnno} - Purchase Return Record Created by {request.user.username}"
        )

        # Update the stock with returned products.
        update_product_stock(Products, ProductVariation, purchase_return_items_data, 'add')

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        #----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Validated PurchaseReturnOrders Data
        purchase_return_orders_data = given_data.pop('purchase_return_orders', None) # parent_data
        if purchase_return_orders_data:
            purchase_return_orders_data['purchase_return_id'] = pk
            return_order_error = validate_multiple_data(self, purchase_return_orders_data , PurchaseReturnOrdersSerializer,['return_no'])
            # validate the 'order_type' in 'purchase_return_orders' data
            validate_order_type(purchase_return_orders_data, return_order_error, OrderTypes,look_up='order_type')

        # Validated PurchaseReturnItems Data
        purchase_return_items_data = given_data.pop('purchase_return_items', None)
        
        if purchase_return_items_data:
            purchase_return_items_data = [
                item for item in purchase_return_items_data
                if item.get("product_id") and item.get("quantity")
            ]
        
        if purchase_return_items_data:
            exclude_fields = ['purchase_return_id']
            return_item_error = validate_put_method_data(self, purchase_return_items_data, PurchaseReturnItemsSerializer, exclude_fields, PurchaseReturnItems, current_model_pk_field='purchase_return_item_id')

        # Validated OrderAttchments Data
        order_attachments_data = given_data.pop('order_attachments', None)
        exclude_fields = ['order_id','order_type_id']
        if order_attachments_data:
            attachment_error = validate_put_method_data(self, order_attachments_data, OrderAttachmentsSerializer, exclude_fields, OrderAttachments, current_model_pk_field='attachment_id')
        else:
            attachment_error = [] # Since 'order_attachments' is optional, so making an error is empty list

        # Validated OrderShipments Data
        order_shipments_data = given_data.pop('order_shipments', None)
        if order_shipments_data:
            shipments_error = validate_put_method_data(self, order_shipments_data, OrderShipmentsSerializer, exclude_fields, OrderShipments, current_model_pk_field='shipment_id')
        else:
            shipments_error = [] # Since 'order_shipments' is optional, so making an error is empty list

        # Validated CustomFieldValues Data
        custom_field_values_data = given_data.pop('custom_field_values', None)
        if custom_field_values_data:
            exclude_fields = ['custom_id']
            custom_field_values_error = validate_put_method_data(self, custom_field_values_data, CustomFieldValueSerializer, exclude_fields, CustomFieldValue, current_model_pk_field='custom_field_value_id')
        else:
            custom_field_values_error = []

        # Ensure mandatory data is present
        if not purchase_return_orders_data or not purchase_return_items_data:
            logger.error("Purchase return order and Purchase return items & CustomFields are mandatory but not provided.")
            return build_response(0, "Purchase return order and Purchase return items & CustomFields are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if return_order_error:
            errors["purchase_return_orders"] = return_order_error
        if return_item_error:
            errors["purchase_return_items"] = return_item_error
        if attachment_error:
            errors['order_attachments'] = attachment_error
        if shipments_error:
            errors['order_shipments'] = shipments_error
        if custom_field_values_error:
            errors['custom_field_values'] = custom_field_values_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)        
      
        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        # update PurchaseReturnOrders
        if purchase_return_orders_data:
            update_fields = [] # No need to update any fields
            purchasereturnorder_data = update_multi_instances(self, pk, purchase_return_orders_data, PurchaseReturnOrders, PurchaseReturnOrdersSerializer, update_fields,main_model_related_field='purchase_return_id', current_model_pk_field='purchase_return_id')
            purchasereturnorder_data = purchasereturnorder_data[0] if len(purchasereturnorder_data)==1 else purchasereturnorder_data

        # Update the 'PurchaseReturnItems'
        update_fields = {'purchase_return_id':pk}
        return_items_data = update_multi_instances(self, pk, purchase_return_items_data, PurchaseReturnItems, PurchaseReturnItemsSerializer, update_fields, main_model_related_field='purchase_return_id', current_model_pk_field='purchase_return_item_id')

        # Get 'order_type_id' from 'OrderTypes' model
        order_type_val = purchase_return_orders_data.get('order_type')
        order_type = get_object_or_none(OrderTypes, name=order_type_val)
        type_id = order_type.order_type_id

        # Update the 'order_attchments'
        update_fields = {'order_id':pk, 'order_type_id':type_id}
        attachment_data = update_multi_instances(self, pk, order_attachments_data, OrderAttachments, OrderAttachmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='attachment_id')

        # Update the 'shipments'
        shipment_data = update_multi_instances(self, pk, order_shipments_data, OrderShipments, OrderShipmentsSerializer, update_fields, main_model_related_field='order_id', current_model_pk_field='shipment_id')
        shipment_data = shipment_data[0] if len(shipment_data)==1 else shipment_data

        # Update CustomFieldValues Data
        if custom_field_values_data:
            custom_field_values_data = update_multi_instances(self, pk, custom_field_values_data, CustomFieldValue, CustomFieldValueSerializer, {}, main_model_related_field='custom_id', current_model_pk_field='custom_field_value_id')

        custom_data = {
            "purchase_return_orders":purchasereturnorder_data,
            "purchase_return_items":return_items_data if return_items_data else [],
            "order_attachments":attachment_data if attachment_data else [],
            "order_shipments":shipment_data if shipment_data else {},
            "custom_field_values": custom_field_values_data if custom_field_values_data else []  # Add custom field values to response
        }
        
        returnno = purchase_return_orders_data.get("return_no")
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "UPDATE",
            "Purchase Return",
            pk,
            f"{returnno} - Purchase Return Record Updated by {request.user.username}"
        )

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

#-------------------- Bill Payments -------------------------------
from rest_framework.views import APIView
from rest_framework import status
from django.db import transaction
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ObjectDoesNotExist
import uuid, traceback


class BillPaymentTransactionAPIView(APIView):
    """
    Handles retrieval of Bill Payment Transactions.
    Supports both single record (via pk) and filtered list retrieval.
    """
    
    def get(self, request, transaction_id=None):
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))

        # ✅ CASE 1: FETCH SINGLE RECORD
        if transaction_id:
            try:
                transaction = BillPaymentTransactions.objects.get(transaction_id=transaction_id)
                serializer = BillPaymentTransactionSerializer(transaction)
                return build_response(1, "Bill Payment Transaction fetched successfully", serializer.data, status.HTTP_200_OK)
            except BillPaymentTransactions.DoesNotExist:
                return build_response(0, "Bill Payment Transaction not found", None, status.HTTP_404_NOT_FOUND)

        # ✅ CASE 2: APPLY FILTERS (INCLUDING GLOBAL SEARCH)
        filtered_qs = BillPaymentTransactionsReportFilter(request.GET, queryset=BillPaymentTransactions.objects.all().order_by('-created_at')).qs

        # ✅ Get total count BEFORE pagination
        # total_count = filtered_qs.count()
        transactions = BillPaymentTransactions.objects.all().order_by('-created_at')

        total_count = transactions.count()

        # ✅ Apply pagination manually
        start = (page - 1) * limit
        end = start + limit
        paginated_qs = filtered_qs[start:end]

        # ✅ No records case
        # if not paginated_qs.exists():
        #     return filter_response(0, "No Bill Payment Transactions found", page, limit, total_count, None, status.HTTP_404_NOT_FOUND)

        serializer = BillPaymentTransactionSerializer(paginated_qs, many=True)

        return filter_response(
            len(serializer.data),
            "Bill Payment Transactions fetched successfully",
            serializer.data,
            page,
            limit,
            total_count,   # ✅ total of all filtered records, not just per page
            status.HTTP_200_OK
        )

    """
    Handles Purchase Bill Payments (Vendor Side)
    - adjustNow → one-to-one invoice payment
    - non-adjustNow → bulk payment allocation across invoices
    """

    def post(self, request):
        data = request.data
        vendor_data = data.get('vendor')
        
        # account_data = data.get('ledger_account')
        
        # Handle both string and dict cases
        if isinstance(vendor_data, dict):
            vendor_id = vendor_data.get('vendor_id') or vendor_data.get('id')
        else:
            vendor_id = vendor_data
            if not vendor_id:
                return build_response(1, "vendor ID is required.", None, status.HTTP_400_BAD_REQUEST)
            vendor_id = vendor_id.replace('-', '')
            
        # Validate vendor_id
        try:
            uuid.UUID(vendor_id)
            Vendor.objects.get(pk=vendor_id)
        except (ValueError, TypeError, Vendor.DoesNotExist) as e:
            return build_response(1, "Invalid vendor ID format OR Vendor does not exist.", str(e), status.HTTP_404_NOT_FOUND)


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

        # Validate FK object properly
        try:
            uuid.UUID(ledger_account_id)
            ledger_account_instance = LedgerAccounts.objects.get(pk=ledger_account_id)
        except (ValueError, TypeError, LedgerAccounts.DoesNotExist) as e:
            return build_response(1, "Invalid Ledger Account ID format OR Ledger Account does not exist.", str(e), status.HTTP_404_NOT_FOUND)

        # This is the correct FK object to use everywhere
        account_id = ledger_account_instance.ledger_account_id

        
        # vendor_id = vendor_data.get('vendor_id').replace('-', '')
        # account_id = account_data.get('account_id').replace('-', '')
        description = data.get('description')
        payment_method = data.get('payment_method', 'CASH')
        payment_receipt_no = data.get('payment_receipt_no')

        # # Validate ledger_account_id
        # try:
        #     uuid.UUID(ledger_account_id)
        #     LedgerAccounts.objects.get(pk=ledger_account_id)
        # except (ValueError, TypeError, LedgerAccounts.DoesNotExist) as e:
        #     return build_response(1, "Invalid account ID format OR Chart Of Account does not exist.", str(e), status.HTTP_404_NOT_FOUND)

        
        # Fetch Pending status
        try:
            pending_status = OrderStatuses.objects.get(status_name="Pending").order_status_id
        except ObjectDoesNotExist:
            return build_response(1, "Required order status 'Pending' not found.", None, status.HTTP_404_NOT_FOUND)

        # ========= Case 1: AdjustNow (specific invoice) =========
        if data.get('adjustNow'):
            data_list = request.data
            if isinstance(data_list, dict):
                data_list = [data_list]
            results = []

            try:
                with transaction.atomic():
                    for data in data_list:
                        try:
                            input_adjustNow = Decimal(data.get('adjustNow', 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                            if input_adjustNow <= 0:
                                return build_response(0, "Adjust Now Amount Must Be Positive.", None, status.HTTP_406_NOT_ACCEPTABLE)
                        except (ValueError, TypeError):
                            return build_response(0, "Invalid Adjust Now Amount Provided.", None, status.HTTP_406_NOT_ACCEPTABLE)

                        try:
                            invoice = PurchaseInvoiceOrders.objects.get(invoice_no=data.get('bill_no'))
                            total_amount = invoice.total_amount
                            bal_amt = invoice.pending_amount
                        except PurchaseInvoiceOrders.DoesNotExist:
                            return build_response(1, f"Purchase Invoice with bill no '{data.get('bill_no')}' does not exist.", None, status.HTTP_404_NOT_FOUND)

                        if invoice.order_status_id.status_name != "Completed":
                            if Decimal(bal_amt).quantize(Decimal('0.01')) == Decimal(data.get('outstanding_amount', 0)).quantize(Decimal('0.01')):
                                outstanding_amount = Decimal(data.get('outstanding_amount', 0))
                                if outstanding_amount == 0:
                                    return build_response(0, "No Outstanding Amount", None, status.HTTP_400_BAD_REQUEST)

                                if input_adjustNow > outstanding_amount:
                                    allocated_amount = outstanding_amount
                                    new_outstanding = Decimal("0.00")
                                    remaining_payment = input_adjustNow - outstanding_amount
                                else:
                                    allocated_amount = input_adjustNow
                                    new_outstanding = outstanding_amount - input_adjustNow
                                    remaining_payment = Decimal("0.00")
                                    
                                # Create Payment Transaction
                                vendor_instance = Vendor.objects.get(pk=vendor_id)
                                ledger_account_instance = LedgerAccounts.objects.get(pk=account_id)

                                bill_payment = BillPaymentTransactions.objects.create(
                                    payment_receipt_no=payment_receipt_no,
                                    payment_method=payment_method,
                                    total_amount=total_amount,
                                    amount=allocated_amount,   # ✅ Add this line
                                    outstanding_amount=new_outstanding,
                                    adjusted_now=allocated_amount,
                                    payment_status=data.get('payment_status', 'Completed'),
                                    purchase_invoice=invoice,
                                    bill_no=invoice.invoice_no,
                                    vendor=vendor_instance,
                                    ledger_account_id=ledger_account_instance
                                )
                                
                                #log action
                                if new_outstanding == 0:
                                    log_user_action(
                                        set_db('default'),
                                        request.user,
                                        "CREATE & UPDATE",
                                        "Bill Payments & Purchase Invoice",
                                        invoice.purchase_invoice_id,
                                        f"{bill_payment.payment_receipt_no} - Payment transaction record created & {invoice.invoice_no} - Invoice marked as Completed by {request.user.username}"
                                    )
                                else:
                                    log_user_action(
                                        set_db('default'),
                                        request.user,
                                        "CREATE",
                                        "Bill Payments",
                                        bill_payment.transaction_id,
                                        f"{bill_payment.payment_receipt_no} - Payment created by {request.user.username}"
                                    )

                                completed_status = OrderStatuses.objects.filter(status_name='Completed').first()
                                if completed_status:
                                    PurchaseInvoiceOrders.objects.filter(purchase_invoice_id=invoice.purchase_invoice_id).update(order_status_id=completed_status.order_status_id)
                                    BillPaymentTransactions.objects.filter(purchase_invoice_id=invoice.purchase_invoice_id).update(payment_status="Completed")

                                journal_entry_line_response = JournalEntryLinesAPIView.post(
                                    self, vendor_id, ledger_account_id, input_adjustNow, description, remaining_payment, payment_receipt_no
                                )
                                vendor_balance_response = VendorBalanceView.post(self, request, vendor_id, remaining_payment)

                                results.append({
                                    "Transaction ID": str(bill_payment.transaction_id),
                                    "Total Invoice Amount": str(total_amount),
                                    "Allocated Amount": str(allocated_amount),
                                    "New Outstanding": str(new_outstanding),
                                    "Bill Payment Receipt No": bill_payment.payment_receipt_no,
                                    "Remaining Payment": str(remaining_payment),
                                    "account_id": str(account_id),
                                    "journal_entry_line": journal_entry_line_response.data.get("message"),
                                    "vendor_balance": vendor_balance_response.data.get("message")
                                })
                            else:
                                return build_response(0, f"Wrong outstanding_amount given, correct amount is {bal_amt}", None, status.HTTP_400_BAD_REQUEST)
                        else:
                            return build_response(0, "Invoice Already Completed", None, status.HTTP_400_BAD_REQUEST)

            except Exception as e:
                traceback.print_exc()
                return build_response(1, "An error occurred", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

            return build_response(len(results), "Bill Payment transactions processed successfully", results, status.HTTP_201_CREATED)

        # ========= Case 2: Non-adjustNow (bulk allocation) =========
        else:
            try:
                input_amount = Decimal(data.get('amount', 0)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                if input_amount <= 0:
                    return build_response(0, "Amount must be positive.", None, status.HTTP_406_NOT_ACCEPTABLE)
            except (ValueError, TypeError):
                return build_response(0, "Invalid Amount Provided.", None, status.HTTP_406_NOT_ACCEPTABLE)

            try:
                with transaction.atomic():
                    # Fetch all pending purchase invoices for this vendor
                    invoices = PurchaseInvoiceOrders.objects.filter(vendor_id=vendor_id).exclude(order_status_id__status_name__in=["Completed", "Cancelled"]).order_by('invoice_date')  # Oldest invoice first
                    if not invoices.exists():
                        return build_response(0, "No pending invoices found for this vendor.", None, status.HTTP_400_BAD_REQUEST)

                    results = []
                    remaining_payment = input_amount

                    for invoice in invoices:
                        if remaining_payment <= 0:
                            break

                        outstanding = Decimal(invoice.pending_amount).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
                        if outstanding <= 0:
                            continue

                        if remaining_payment >= outstanding:
                            allocated_amount = outstanding
                            new_outstanding = Decimal("0.00")
                            remaining_payment -= outstanding
                        else:
                            allocated_amount = remaining_payment
                            new_outstanding = outstanding - remaining_payment
                            remaining_payment = Decimal("0.00")

                        # Create Payment Transaction
                        vendor_instance = Vendor.objects.get(pk=vendor_id)
                        ledger_account_instance = LedgerAccounts.objects.get(pk=account_id)
                        
                        bill_payment = BillPaymentTransactions.objects.create(
                            payment_receipt_no=payment_receipt_no,
                            payment_method=payment_method,
                            total_amount=invoice.total_amount,
                            amount=allocated_amount,   # ✅ Add this line
                            outstanding_amount=new_outstanding,
                            adjusted_now=allocated_amount,
                            payment_status='Completed' if new_outstanding == 0 else 'Pending',
                            purchase_invoice=invoice,
                            bill_no=invoice.invoice_no,
                            vendor=vendor_instance,
                            ledger_account_id=ledger_account_instance
                        )
                        
                        #log action
                        if new_outstanding == 0:
                            log_user_action(
                                set_db('default'),
                                request.user,
                                "CREATE & UPDATE",
                                "Bill Payments & Purchase Invoice",
                                invoice.purchase_invoice_id,
                                f"{bill_payment.payment_receipt_no} - Payment transaction record created & {invoice.invoice_no} - Invoice marked as Completed by {request.user.username}"
                            )
                        else:
                            log_user_action(
                                set_db('default'),
                                request.user,
                                "CREATE",
                                "Bill Payments",
                                bill_payment.transaction_id,
                                f"{bill_payment.payment_receipt_no} - Payment created by {request.user.username}"
                            )
                        
                        # invoice.update_paid_amount_and_pending_amount_after_bill_payment(
                        #     payment_amount=allocated_amount,
                        #     outstanding_amount=new_outstanding
                        # )


                        # if invoice.pending_amount == 0:
                        #     completed_status = OrderStatuses.objects.filter(status_name='Completed').first()
                        #     if completed_status:
                        #         invoice.order_status_id = completed_status
                        #         BillPaymentTransactions.objects.filter(purchase_invoice_id=invoice.purchase_invoice_id).update(payment_status="Completed")

                        # invoice.save()

                        if new_outstanding == 0:
                            completed_status = OrderStatuses.objects.filter(status_name='Completed').first()
                            if completed_status:
                                PurchaseInvoiceOrders.objects.filter(purchase_invoice_id=invoice.purchase_invoice_id).update(order_status_id=completed_status.order_status_id)
                                BillPaymentTransactions.objects.filter(purchase_invoice_id=invoice.purchase_invoice_id).update(payment_status="Completed")

                        results.append({
                            "Transaction ID": str(bill_payment.transaction_id),
                            "Invoice No": invoice.invoice_no,
                            "Total Invoice Amount": str(invoice.total_amount),
                            "Allocated Amount": str(allocated_amount),
                            "New Outstanding": str(new_outstanding),
                            "Remaining Payment": str(remaining_payment),
                            "Payment Status": bill_payment.payment_status,
                        })

                    # Post journal + update balance
                    journal_entry_line_response = JournalEntryLinesAPIView.post(
                        self, vendor_id, ledger_account_id, input_amount, description, remaining_payment, payment_receipt_no
                    )
                    vendor_balance_response = VendorBalanceView.post(self, request, vendor_id, remaining_payment)

            except Exception as e:
                traceback.print_exc()
                return build_response(1, "Error processing bulk bill payments", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)

            return build_response(len(results), "Bill Payment transactions processed successfully", {
                "processed_invoices": results,
                "journal_entry_line": journal_entry_line_response.data.get("message"),
                "vendor_balance": vendor_balance_response.data.get("message")
            }, status.HTTP_201_CREATED)
            
    def put(self, request, transaction_id):
        with transaction.atomic():
            try:
                pending_status = OrderStatuses.objects.get(status_name="Pending")
                completed_status = OrderStatuses.objects.get(status_name="Completed")
            except ObjectDoesNotExist:
                return build_response(
                    1,
                    "Required order statuses 'Pending' or 'Completed' not found.",
                    None,
                    status.HTTP_404_NOT_FOUND
                )

            # Step 1: Get Bill Payment Transaction record
            bill_payment = get_object_or_404(BillPaymentTransactions, transaction_id=transaction_id)
            
            # === New validation for Completed status ===
            if bill_payment.payment_status == "Completed":
                return build_response(
                    0,
                    "This transaction is already completed and cannot be updated.",
                    None,
                    status.HTTP_400_BAD_REQUEST
                )
                
            old_amount = bill_payment.amount or Decimal("0.00")
            old_adjusted = bill_payment.adjusted_now or Decimal("0.00")
            old_outstanding = bill_payment.outstanding_amount or Decimal("0.00")

            # Step 2: Extract new values
            new_amount = Decimal(request.data.get("amount")).quantize(Decimal("0.01"))
            adjusted_now = Decimal(request.data.get("adjusted_now", bill_payment.adjusted_now)).quantize(Decimal("0.01"))
            payment_method = request.data.get("payment_method", bill_payment.payment_method)
            payment_status = request.data.get("payment_status", bill_payment.payment_status)
            payment_receipt_no = request.data.get("payment_receipt_no", bill_payment.payment_receipt_no)

            # Step 3: Get related purchase invoice
            invoice = bill_payment.purchase_invoice
            all_txns = BillPaymentTransactions.objects.filter(purchase_invoice=invoice)

            # Step 4: Calculate sum excluding this record to avoid duplication
            total_of_amount = (
                BillPaymentTransactions.objects.filter(purchase_invoice=invoice)
                .exclude(payment_receipt_no=payment_receipt_no)
                .aggregate(total_amount=Sum("amount"))
                .get("total_amount") or Decimal("0.00")
            )

            max_allowed = invoice.total_amount - total_of_amount
            if new_amount > max_allowed:
                return build_response(
                    1,
                    f"Overpayment detected. Max allowed: ₹{max_allowed}",
                    None,
                    status.HTTP_422_UNPROCESSABLE_ENTITY
                )

            # === Step 5: Delta adjustment for outstanding amount ===
            # payment_diff = adjusted_now - old_adjusted
            # new_outstanding = (old_outstanding - payment_diff).quantize(Decimal("0.01"))
            amount_diff = new_amount - old_amount
            adjusted_diff = adjusted_now - old_adjusted

            # The effective difference to subtract from outstanding
            effective_diff = amount_diff if amount_diff != 0 else adjusted_diff

            new_outstanding = (old_outstanding - effective_diff).quantize(Decimal("0.01"))

            # Prevent negative values
            if new_outstanding < 0:
                new_outstanding = Decimal("0.00")
            # Prevent negative values
            if new_outstanding < 0:
                new_outstanding = Decimal("0.00")

            # === Step 6: Update payment transaction ===
            bill_payment.amount = new_amount
            bill_payment.adjusted_now = adjusted_now
            bill_payment.outstanding_amount = new_outstanding
            bill_payment.payment_status = payment_status
            bill_payment.payment_method = payment_method
            bill_payment.payment_receipt_no = payment_receipt_no
            bill_payment.save()

            # === Step 7: Update invoice totals ===
            paid = all_txns.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")
            invoice.paid_amount = paid
            invoice.pending_amount = new_outstanding
            invoice.order_status_id = completed_status if new_outstanding == 0 else pending_status
            invoice.save(update_fields=["paid_amount", "pending_amount", "order_status_id"])

            # === Step 8: Update Journal Entries ===
            # Fetch ledger account used in original payment
            account_instance = bill_payment.ledger_account_id

            vendor_instance = bill_payment.vendor

            # Get latest balance
            existing_balance = (
                JournalEntryLines.objects.filter(vendor_id=vendor_instance.vendor_id)
                .order_by("-created_at")
                .values_list("balance", flat=True)
                .first()
            ) or Decimal("0.00")

            reversal_balance = old_amount + existing_balance

            # Reversal entry
            JournalEntryLines.objects.create(
                ledger_account_id=account_instance,
                debit=old_amount,
                voucher_no=payment_receipt_no,
                credit=Decimal("0.00"),
                description=f"Reversal of wrong entry for bill receipt {payment_receipt_no} - System Generated Entry",
                vendor_id=vendor_instance,
                balance=reversal_balance,
            )

            time.sleep(1)

            total_related = (
                BillPaymentTransactions.objects.filter(payment_receipt_no=payment_receipt_no)
                .exclude(purchase_invoice=invoice)
                .aggregate(total=Sum("amount"))["total"]
                or Decimal("0.00")
            )

            final_addition = total_related + new_amount
            total_pending = (reversal_balance - new_amount).quantize(Decimal("0.01"))

            # Create revision entry
            JournalEntryLines.objects.create(
                ledger_account_id=account_instance,
                debit=Decimal("0.00"),
                voucher_no=payment_receipt_no,
                credit=final_addition,
                description=f"Updated bill receipt {payment_receipt_no} for Invoice {invoice.invoice_no} - revision recorded",
                vendor_id=vendor_instance,
                balance=total_pending,
            )

            # === Step 9: Prepare response ===
            response_data = {
                "payment_receipt_no": bill_payment.payment_receipt_no,
                "bill_no": invoice.invoice_no,
                "paid_amount": invoice.paid_amount,
                "pending_amount": invoice.pending_amount,
                "outstanding_amount": new_outstanding,
                "payment_status": payment_status,
            }

            return build_response(1, "Bill Payment Transaction updated successfully.", response_data, status.HTTP_200_OK)


class FetchPurchaseInvoicesForPaymentReceiptTable(APIView):
    '''This API is used to fetch all information related to sales invoices for 
        the Payment Receipt. It's related to the Payment Transaction table only.'''
    def get(self, request, vendor_id):
        
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        
        purchase_invoice = PurchaseInvoiceOrders.objects.filter(vendor_id=vendor_id)
        
        if not purchase_invoice.exists():
            return build_response(0, "No Purchase invoice found for this customer", None, status.HTTP_400_BAD_REQUEST) 

        try:
            serializer = PurchaseInvoiceOrdersSerializer(purchase_invoice, many=True)
            sorted_data = sorted(
                serializer.data,
                key=lambda x: x['created_at']
            )
            
            total_count = len(serializer.data)
            return filter_response(total_count, "Purchase Invoices", sorted_data, page, limit, total_count, status.HTTP_200_OK)
            # return filter_response(len(serializer.data), "Purchase Invoices", sorted_data, status.HTTP_200_OK)
        except Exception as e:
            return build_response(0, "An error occurred", str(e), status.HTTP_500_INTERNAL_SERVER_ERROR)


#Barcode - logic --------------- 

from rest_framework.decorators import api_view
from rest_framework import status
# from apps.products.utils.barcode_utils import get_product_by_barcode
from apps.products.serializers import ProductOptionsSerializer
# from apps.common.utils import build_response

@api_view(['GET'])
def scan_purchase_barcode(request):
    barcode_value = request.query_params.get("barcode")

    product = get_product_by_barcode(barcode_value, mode="IN")
    if not product:
        return build_response(0, "Invalid entry barcode", [], status.HTTP_404_NOT_FOUND)

    serializer = ProductOptionsSerializer(product)
    return build_response(1, "Product fetched successfully", serializer.data, status.HTTP_200_OK)
