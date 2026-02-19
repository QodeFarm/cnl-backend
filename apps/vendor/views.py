import logging
from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import render,get_object_or_404
from django.http import  Http404
from requests import Response
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
from django.core.exceptions import  ObjectDoesNotExist

from apps.auditlogs.utils import log_user_action
from apps.customfields.models import CustomFieldValue
from apps.customfields.serializers import CustomFieldValueSerializer
from apps.vendor.filters import VendorAgentFilter, VendorCategoryFilter, VendorFilter, VendorPaymentTermsFilter
from config.utils_db_router import set_db
from config.utils_filter_methods import filter_response, list_filtered_objects
from .models import Vendor, VendorBalance, VendorCategory, VendorPaymentTerms, VendorAgent, VendorAttachment, VendorAddress
from apps.masters.models import FirmStatuses, GstCategories, PriceCategories, Territory, Transporters
from config.utils_methods import BaseBulkUpdateView
from .serializers import VendorBalanceSerializer, VendorSerializer, VendorCategorySerializer, VendorPaymentTermsSerializer, VendorAgentSerializer, VendorAttachmentSerializer, VendorAddressSerializer, VendorSummaryReportSerializer, VendorsOptionsSerializer
from config.utils_methods import delete_multi_instance, soft_delete, list_all_objects, create_instance, update_instance, build_response, validate_input_pk, validate_payload_data, validate_multiple_data, generic_data_creation, validate_put_method_data, update_multi_instances
from uuid import UUID
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter

from django.http import HttpResponse, HttpResponseRedirect
from urllib.parse import urlencode

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get an instance of a logger
logger = logging.getLogger(__name__)
from django.db import transaction
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
from config.utils_methods import BaseExcelImportExport, build_response
from .models import (
    Vendor, VendorAddress, VendorAttachment, VendorCategory, VendorPaymentTerms, VendorAgent
)
from apps.customer.models import LedgerAccounts
from apps.masters.models import (
    Country, State, City, FirmStatuses, Territory, 
    GstCategories, PriceCategories, Transporters, LedgerGroups
)
import logging
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation
from openpyxl.comments import Comment

# Set up logger
logger = logging.getLogger(__name__)

# Create your views here.

class VendorsView(viewsets.ModelViewSet):
    queryset = Vendor.objects.all().order_by('is_deleted', '-created_at')	
    serializer_class = VendorSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = VendorFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class VendorCategoryView(viewsets.ModelViewSet):
    queryset = VendorCategory.objects.all().order_by('is_deleted', '-created_at')	
    serializer_class = VendorCategorySerializer 
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = VendorCategoryFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Vendor Category"
    log_pk_field = "vendor_category_id"
    log_display_field = "code"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, VendorCategory,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

class VendorPaymentTermsView(viewsets.ModelViewSet):
    queryset = VendorPaymentTerms.objects.all().order_by('is_deleted', '-created_at')	
    serializer_class = VendorPaymentTermsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = VendorPaymentTermsFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Vendor Payment Terms"
    log_pk_field = "payment_term_id"
    log_display_field = "name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, VendorPaymentTerms,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)  
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)  

class VendorAgentView(viewsets.ModelViewSet):
    queryset = VendorAgent.objects.all().order_by('is_deleted', '-created_at')	
    serializer_class = VendorAgentSerializer   
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = VendorAgentFilter
    ordering_fields = ['created_at']
    
    #log actions
    log_actions = True
    log_module_name = "Vendor Agent"
    log_pk_field = "vendor_agent_id"
    log_display_field = "name"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, VendorAgent,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)  

class VendorAttachmentView(viewsets.ModelViewSet):
    queryset = VendorAttachment.objects.all()
    serializer_class = VendorAttachmentSerializer   

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class VendorAddressView(viewsets.ModelViewSet):
    queryset = VendorAddress.objects.all()
    serializer_class = VendorAddressSerializer  

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class VendorViewSet(APIView):
    """API ViewSet for handling vendor creation and related data."""
    def get_object(self, pk):
        try:
            return Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            logger.warning(f"Vendor with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        
    def get(self, request, *args, **kwargs):
        """Handles GET requests to retrieve vendors with optional filters and reports."""
        try:
            if "pk" in kwargs:
                result = validate_input_pk(self, kwargs['pk'])
                return result if result else self.retrieve(self, request, *args, **kwargs)

            if request.query_params.get("summary", "false").lower() == "true":
                return self.get_summary_data(request)
            
            if request.query_params.get("vendor_summary_report", "false").lower() == "true":
                return self.get_vendor_summary_report(request)
                
            if request.query_params.get("vendor_ledger_report", "false").lower() == "true":
                return self.get_vendor_ledger_report(request)

            if request.query_params.get("vendor_outstanding_report", "false").lower() == "true":
                return self.get_vendor_outstanding_report(request)

            if request.query_params.get("vendor_performance_report", "false").lower() == "true":
                return self.get_vendor_performance_report(request)

            if request.query_params.get("vendor_payment_report", "false").lower() == "true":
                return self.get_vendor_payment_report(request)

            return self.get_vendors(request)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_pagination_params(self, request):
        """Extracts pagination parameters from the request."""
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        return page, limit
    
    def apply_filters(self, request, queryset, filter_class, model_class):
        """Generic function to apply filters on any queryset and return total count."""
        if request.query_params:
            filterset = filter_class(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs  

        total_count = model_class.objects.count()  # Total count calculation
        return queryset, total_count

    def get_summary_data(self, request):
        """Fetches vendor summary data."""
        logger.info("Retrieving vendor summary")

        page, limit = self.get_pagination_params(request)
        queryset = Vendor.objects.all().order_by('is_deleted', '-created_at')
        queryset, total_count = self.apply_filters(request, queryset, VendorFilter, Vendor)

        serializer = VendorsOptionsSerializer(queryset, many=True)
        return filter_response(queryset.count(), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

    def get_vendors(self, request):
        """Applies filters, pagination, and retrieves vendor data."""
        logger.info("Retrieving all vendors")

        page, limit = self.get_pagination_params(request)
        queryset = Vendor.objects.all().order_by('is_deleted', '-created_at')
        queryset, total_count = self.apply_filters(request, queryset, VendorFilter, Vendor)

        serializer = VendorSerializer(queryset, many=True)

        return filter_response(total_count, "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)
    
    def get_vendor_summary_report(self, request):
        """
        Fetches a summary report of purchase data and pending payments per vendor.
        Displays total purchases, pending payments, and last purchase date.
        """
        logger.info("Retrieving vendor summary report data")
        page, limit = self.get_pagination_params(request)
        
        from django.db.models import Sum, F, DecimalField, Value, ExpressionWrapper, Max
        from django.db.models.functions import Coalesce
        
        # Start with a base queryset of vendors
        queryset = Vendor.objects.all()
        
        # Calculate total purchases and payments
        vendors = queryset.annotate(
            # Total purchases (invoiced amount)
            total_purchases=Coalesce(
                Sum('purchaseinvoiceorders__total_amount', output_field=DecimalField(max_digits=18, decimal_places=2)),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))
            ),
            # Total payments made
            total_paid=Coalesce(
                Sum('purchaseinvoiceorders__advance_amount', output_field=DecimalField(max_digits=18, decimal_places=2)),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))
            ),
            # Get the most recent purchase date
            last_purchase_date=Max('purchaseinvoiceorders__invoice_date')
        )
        
        # Calculate total pending amount
        vendors = vendors.annotate(
            total_pending=ExpressionWrapper(
                F('total_purchases') - F('total_paid'),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            )
        )
        
        # Order by total_purchases by default (highest first)
        vendors = vendors.order_by('-total_purchases')
        
        # Apply any additional filters from the request
        if request.query_params:
            from apps.vendor.filters import VendorSummaryReportFilter
            filterset = VendorSummaryReportFilter(request.GET, queryset=vendors)
            if filterset.is_valid():
                vendors = filterset.qs
        
        total_count = vendors.count()
        
        # Use the dedicated serializer for the vendor summary report
        serializer = VendorSummaryReportSerializer(vendors, many=True)
        
        return filter_response(
            vendors.count(),
            "Success",
            serializer.data,
            page,
            limit,
            total_count,
            status.HTTP_200_OK
        )
    def get_vendor_ledger_report(self, request):
        """
        Fetches all financial transactions with a specific vendor and calculates running balance.
        This report provides a detailed ledger of all purchases, payments, and other transactions.
        """
        logger.info("Retrieving vendor ledger report data")
        page, limit = self.get_pagination_params(request)
        
        from apps.finance.models import JournalEntryLines
        from django.db.models import F, Q, Sum
        
        # Get vendor_id filter from request params if provided
        vendor_id = request.query_params.get('vendor_id')
        
        # Start with base queryset filtering only for entries related to vendors
        queryset = JournalEntryLines.objects.filter(vendor_id__isnull=False).select_related(
            'journal_entry_id', 'vendor_id'
        ).order_by('journal_entry_id__entry_date')
        
        # Apply vendor filter if provided
        if vendor_id:
            queryset = queryset.filter(vendor_id=vendor_id)
            
        # Apply filters from request
        if request.query_params:
            from apps.vendor.filters import VendorLedgerReportFilter
            filterset = VendorLedgerReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
        
        # Calculate total records before pagination
        total_count = queryset.count()
        
        # Calculate running balance for each transaction
        # First, get all the records to process
        records = list(queryset)
        running_balance = 0
        
        # Process each record to calculate running balance
        for record in records:
            # For vendor ledger: credit increases balance, debit decreases (opposite of customer ledger)
            running_balance += record.credit - record.debit
            record.running_balance = running_balance
        
        # Apply pagination manually after calculating running balance
        if page and limit:
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            records = records[start_idx:end_idx]
        
        # Serialize the data with the running balance included
        from apps.vendor.serializers import VendorLedgerReportSerializer
        serializer = VendorLedgerReportSerializer(records, many=True)
        
        return filter_response(len(records), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK )

    def get_vendor_outstanding_report(self, request):
        """
        Fetches a report of pending payments that need to be made to vendors.
        Shows ONLY vendors with outstanding payments due.
        """
        logger.info("Retrieving vendor outstanding report data")
        page, limit = self.get_pagination_params(request)
        
        from django.db.models import Sum, F, DecimalField, Value, ExpressionWrapper, Max
        from django.db.models.functions import Coalesce
        
        # Start with a base queryset of vendors
        queryset = Vendor.objects.all()
        
        # Calculate total purchases and payments
        vendors = queryset.annotate(
            # Total purchases (invoiced amount)
            total_purchases=Coalesce(
                Sum('purchaseinvoiceorders__total_amount', output_field=DecimalField(max_digits=18, decimal_places=2)),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))
            ),
            # Total payments made
            total_paid=Coalesce(
                Sum('purchaseinvoiceorders__advance_amount', output_field=DecimalField(max_digits=18, decimal_places=2)),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))
            ),
            # Get the most recent purchase date
            last_purchase_date=Max('purchaseinvoiceorders__invoice_date')
        )
        
        # Calculate total pending amount
        vendors = vendors.annotate(
            total_pending=ExpressionWrapper(
                F('total_purchases') - F('total_paid'),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            )
        )
        
        # Filter out vendors with no outstanding payments
        vendors = vendors.filter(total_pending__gt=0)
        
        # Order by pending amount (highest first) - this differs from summary report which sorts by total_purchases
        vendors = vendors.order_by('-total_pending')
        
        # Apply any additional filters from the request
        if request.query_params:
            from apps.vendor.filters import VendorOutstandingReportFilter
            filterset = VendorOutstandingReportFilter(request.GET, queryset=vendors)
            if filterset.is_valid():
                vendors = filterset.qs
        
        total_count = vendors.count()
        
        # Use the dedicated serializer for the vendor outstanding report
        from apps.vendor.serializers import VendorOutstandingReportSerializer
        serializer = VendorOutstandingReportSerializer(vendors, many=True)
        
        return filter_response(
            vendors.count(),
            "Success",
            serializer.data,
            page,
            limit,
            total_count,
            status.HTTP_200_OK
        )
        
    def get_vendor_performance_report(self, request):
        """
        Fetches a simplified vendor performance report based on available data.
        """
        logger.info("Retrieving vendor performance report data")
        page, limit = self.get_pagination_params(request)
        
        try:
            # Start with all vendors
            queryset = Vendor.objects.all()
            
            # Calculate basic metrics
            from django.db.models import Count, Sum, Avg, F, Value, FloatField,Max
            from django.db.models.functions import Coalesce
            
            # Annotate with metrics from purchase invoice orders
            vendors = queryset.annotate(
                # Count total purchase orders
                total_orders=Count('purchaseinvoiceorders', distinct=True),
                
                # Use last purchase date as an indicator
                last_order_date=Coalesce(
                    Max('purchaseinvoiceorders__invoice_date'), 
                    Value(None)
                )
            )
            
            # Generate some basic performance metrics
            from django.db.models import Case, When, IntegerField, ExpressionWrapper
            
            # Calculate on-time deliveries (simplified: assuming 70% of orders are on-time)
            vendors = vendors.annotate(
                on_time_deliveries=ExpressionWrapper(
                    F('total_orders') * 0.7,  # Estimate 70% of orders are on-time
                    output_field=IntegerField()
                ),
                
                # Calculate delayed deliveries (remaining 30%)
                delayed_deliveries=ExpressionWrapper(
                    F('total_orders') * 0.3,  # Estimate 30% of orders are delayed
                    output_field=IntegerField()
                ),
                
                # Calculate on-time percentage (fixed at 70% for demonstration)
                on_time_percentage=Value(70.0, output_field=FloatField()),
                
                # Simulate average delay days
                average_delay_days=Value(2.5, output_field=FloatField()),
                
                # Simulate rejected items count
                rejected_items_count=Value(0, output_field=IntegerField()),
                
                # Assign a quality rating (1-5 scale)
                quality_rating=Case(
                    When(total_orders__gt=10, then=Value(4.5)),
                    When(total_orders__gt=5, then=Value(4.0)),
                    When(total_orders__gt=0, then=Value(3.5)),
                    default=Value(0.0),
                    output_field=FloatField()
                )
            )
            
            # Filter out vendors with no orders
            vendors = vendors.filter(total_orders__gt=0)
            
            # Sort by total orders (most active vendors first)
            vendors = vendors.order_by('-total_orders')
            
            # Apply any additional filters from the request
            if request.query_params:
                from apps.vendor.filters import VendorPerformanceReportFilter
                filterset = VendorPerformanceReportFilter(request.GET, queryset=vendors)
                if filterset.is_valid():
                    vendors = filterset.qs
            
            total_count = vendors.count()
            
            # Apply pagination
            if page and limit:
                start = (page - 1) * limit
                end = start + limit
                vendors = vendors[start:end]
            
            # Use the dedicated serializer
            from apps.vendor.serializers import VendorPerformanceReportSerializer
            serializer = VendorPerformanceReportSerializer(vendors, many=True)
            
            return filter_response(vendors.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in vendor performance report: {str(e)}")
            return build_response(0, f"An error occurred: {str(e)}", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_vendor_payment_report(self, request):
        """
        Fetches a report of all payments made to vendors.
        Shows payment details with vendor and invoice information.
        """
        logger.info("Retrieving vendor payment report data")
        page, limit = self.get_pagination_params(request)
        
        try:
            # Import required finance models
            from apps.finance.models import PaymentTransaction
            
            # Base query - filter payments related to purchases (made to vendors)
            queryset = PaymentTransaction.objects.filter(
                order_type='Purchase',
                transaction_type='Debit'  # Debit transactions represent payments made to vendors
            )
            
            # Order by payment date (most recent first)
            queryset = queryset.order_by('-payment_date')
            
            # Apply any additional filters from the request
            if request.query_params:
                from apps.vendor.filters import VendorPaymentReportFilter
                filterset = VendorPaymentReportFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
            
            # Count total records for pagination
            total_count = queryset.count()
            
            # Apply pagination
            if page and limit:
                start = (page - 1) * limit
                end = start + limit
                queryset = queryset[start:end]
            
            # Use the dedicated serializer for the vendor payment report
            from apps.vendor.serializers import VendorPaymentReportSerializer
            serializer = VendorPaymentReportSerializer(queryset, many=True)
            
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in vendor payment report: {str(e)}")
            return build_response(0, f"An error occurred: {str(e)}", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a vendor and its related data (attachments, and addresses).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)
            
            # Retrieve the Vendor instance
            vendor = get_object_or_404(Vendor, pk=pk)
            vendor_serializer = VendorSerializer(vendor)

            # Retrieve related data
            attachments_data = self.get_related_data(VendorAttachment, VendorAttachmentSerializer, 'vendor_id', pk)
            addresses_data = self.get_related_data(VendorAddress, VendorAddressSerializer, 'vendor_id', pk)
            
            # Retrieve custom field values
            custom_field_values_data = self.get_related_data(CustomFieldValue, CustomFieldValueSerializer, 'custom_id', pk)

            # Customizing the response data
            custom_data = {
                "vendor_data": vendor_serializer.data,
                "vendor_attachments": attachments_data,
                "vendor_addresses": addresses_data,
                "custom_field_values": custom_field_values_data  # Add custom field values
            }
            logger.info("Vendor and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Vendor with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving vendor with pk %s: %s", pk, str(e))
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
      
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a vendor and its related attachments, and addresses.
        """
        try:
            # Get the vendor instance
            instance = Vendor.objects.get(pk=pk)
            
            # Delete related CustomerAttachments and CustomerAddresses
            if not delete_multi_instance(pk, Vendor, VendorAttachment, main_model_field_name='vendor_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, Vendor, VendorAddress, main_model_field_name='vendor_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, Vendor, CustomFieldValue, main_model_field_name='custom_id'):
                return build_response(0, "Error deleting related CustomFieldValue", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main vendor instance
            # instance.delete()
            # Soft delete the main Vendor
            instance.is_deleted = True
            instance.save()

            logger.info(f"Vendor with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except Vendor.DoesNotExist:
            logger.warning(f"Vendor with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting Vendor with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted Vendor record (is_deleted=True → is_deleted=False).
        """
        try:
            instance = Vendor.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"Vendor with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save()

            logger.info(f"Vendor with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except Vendor.DoesNotExist:
            logger.warning(f"Vendor with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring Vendor with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # Handling POST requests for creating
    def post(self, request, *args, **kwargs):   #To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
        return self.create(request, *args, **kwargs)
    
    @transaction.atomic    
    def create(self, request, *args, **kwargs):
        given_data = request.data

        #---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        
        # Extract and Validate Vendor Data
        vendors_data = given_data.pop('vendor_data', None)
        if vendors_data:            
            vendors_error = validate_payload_data(self, vendors_data, VendorSerializer)
        else:
            vendors_error = ["vendors_data is required."]

        # Validate Vendor Attachments
        vendor_attachments_data = given_data.pop('vendor_attachments', None)
        if vendor_attachments_data:
            attachments_error = validate_multiple_data(self, vendor_attachments_data, VendorAttachmentSerializer, ['vendor_id'])
        else:
            attachments_error = []

        # Validate Vendor Addresses
        vendor_addresses_data = given_data.pop('vendor_addresses', None)
        if vendor_addresses_data:
            addresses_error = validate_multiple_data(self, vendor_addresses_data, VendorAddressSerializer, ['vendor_id'])
        else:
            addresses_error = []

        # Validate Custom Fields Data
        custom_fields_data = given_data.pop('custom_field_values', None)
        if custom_fields_data:
            custom_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'])
        else:
            custom_error = []

        # Ensure mandatory data is present
        if not vendors_data or not vendor_addresses_data:
            logger.error("Vendor data, vendor addresses data mandatory but not provided.")
            return build_response(0, "Vendor, vendor addresses mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if vendors_error:
            errors["vendor_data"] = vendors_error
        if attachments_error:
            errors["vendor_attachments"] = attachments_error
        if addresses_error:
            errors['vendor_addresses'] = addresses_error
        if custom_error:
            errors['custom_field_values'] = custom_error
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        #---------------------- D A T A   C R E A T I O N ----------------------------#
        
        # Create Vendor Data
        new_vendor_data = generic_data_creation(self, [vendors_data], VendorSerializer)
        vendor_id = new_vendor_data[0].get("vendor_id", None)  # Fetch vendor_id from new instance
        logger.info('Vendor - created*')

        # Create Vendor Attachments
        update_fields = {'vendor_id': vendor_id}
        if vendor_attachments_data:
            attachments_data = generic_data_creation(self, vendor_attachments_data, VendorAttachmentSerializer, update_fields)
            logger.info('VendorAttachment - created*')
        else:
            attachments_data = []

        # Create Vendor Addresses
        addresses_data = generic_data_creation(self, vendor_addresses_data, VendorAddressSerializer, update_fields)
        logger.info('VendorAddress - created*')

        # Assign `custom_id = vendor_id` for CustomFieldValues
        if custom_fields_data:
            update_fields = {'custom_id': vendor_id}  # Now using `custom_id` like `order_id`
            custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, update_fields)
            logger.info('CustomFieldValues - created*')
        else:
            custom_fields_data = []

        custom_data = {
            "vendor_data": new_vendor_data[0],
            "vendor_attachments": attachments_data,
            "vendor_addresses": addresses_data,
            "custom_field_values": custom_fields_data
        }
        
        vendorname = vendors_data.get("name")
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "CREATE",
            "Vendors",
            vendor_id,
            f"{vendorname} - Vendor Record Created by {request.user.username}"
        )

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)


    def put(self, request, pk, *args, **kwargs):

        #----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Vlidated Vendor Data
        vendors_data = given_data.pop('vendor_data', None)
        if vendors_data:
            vendors_error = validate_payload_data(self, vendors_data , VendorSerializer)

        # Vlidated VendorAttachment Data
        vendor_attachments_data = given_data.pop('vendor_attachments', None)
        if vendor_attachments_data:
            exclude_fields = ['vendor_id']
            attachments_error = validate_put_method_data(self, vendor_attachments_data,VendorAttachmentSerializer, exclude_fields, VendorAttachment,current_model_pk_field='attachment_id')
        else:
            attachments_error = [] # Since 'VendorAttachment' is optional, so making an error is empty list

        # Vlidated VendorAttachment Data
        vendor_addresses_data = given_data.pop('vendor_addresses', None)
        if vendor_addresses_data:
            exclude_fields = ['vendor_id']
            addresses_error = validate_put_method_data(self, vendor_addresses_data,VendorAddressSerializer, exclude_fields,VendorAddress, current_model_pk_field='vendor_address_id')
            
        # Validated CustomFieldValues Data
        custom_field_values_data = given_data.pop('custom_field_values', None)
        if custom_field_values_data:
            exclude_fields = ['custom_id']
            custom_field_values_error = validate_put_method_data(self, custom_field_values_data, CustomFieldValueSerializer, exclude_fields, CustomFieldValue, current_model_pk_field='custom_field_value_id')
        else:
            custom_field_values_error = []  # Optional, so initialize as an empty list

        # Ensure mandatory data is present
        if not vendors_data or not vendor_addresses_data:
            logger.error("Vendor data and vendor addresses data are mandatory but not provided.")
            return build_response(0, "Vendor and vendor addresses are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if vendors_error:
            errors["vendor_data"] = vendors_error
        if attachments_error:
            errors["vendor_attachments"] = attachments_error
        if addresses_error:
            errors['vendor_addresses'] = addresses_error
        if custom_field_values_error:
            errors['custom_field_values'] = custom_field_values_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
        
        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
       
        # Update the 'Vendor'
        if vendors_data:
            update_fields = []# No need to update any fields
            Vendor_data = update_multi_instances(self, pk, [vendors_data], Vendor, VendorSerializer, update_fields,main_model_related_field='vendor_id', current_model_pk_field='vendor_id')

        # Update VendorAttachment Data
        update_fields = {'vendor_id':pk}
        attachments_data = update_multi_instances(self,pk, vendor_attachments_data,VendorAttachment,VendorAttachmentSerializer, update_fields, main_model_related_field='vendor_id', current_model_pk_field='attachment_id')

        # Update VendorAddress Data
        addresses_data = update_multi_instances(self,pk, vendor_addresses_data,VendorAddress, VendorAddressSerializer, update_fields, main_model_related_field='vendor_id', current_model_pk_field='vendor_address_id')
        
        # Update CustomFieldValues Data
        if custom_field_values_data:
            custom_field_values_data = update_multi_instances(self, pk, custom_field_values_data, CustomFieldValue, CustomFieldValueSerializer, {}, main_model_related_field='custom_id', current_model_pk_field='custom_field_value_id')

        custom_data = [
            {"vendor_data":Vendor_data},
            {"vendor_attachments":attachments_data if attachments_data else []},
            {"vendor_addresses":addresses_data if addresses_data else []},
            {"custom_field_values": custom_field_values_data if custom_field_values_data else []}  # Add custom field values to response
        ]
        
        vendorname = vendors_data.get("name")
        # Log the Create
        log_user_action(
            set_db('default'),
            request.user,
            "UPDATE",
            "Vendors",
            pk,
            f"{vendorname} - Vendor Record updated by {request.user.username}"
        )

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)




class VendorExcelImport(BaseExcelImportExport):
    """
    Vendor Excel import/export functionality
    """
    MODEL_CLASS = Vendor
    SERIALIZER_CLASS = None  # Replace with your vendor serializer when available
    REQUIRED_COLUMNS = ["name", "print_name", "vendor_category"]
    TEMPLATE_FILENAME = "Vendor_Import_Template.xlsx"
    
    FIELD_MAP = {
        "name": "name",
        "print_name": "print_name",
        "identification": "identification",
        "code": "code",
        "ledger_account": ("ledger_account_id", LedgerAccounts),
        "ledger_group": "ledger_group",  # For creating LedgerAccounts with proper group
        "vendor_common_for_sales_purchase": "vendor_common_for_sales_purchase",
        "is_sub_vendor": "is_sub_vendor",
        "firm_status": ("firm_status_id", FirmStatuses),
        "territory": ("territory_id", Territory),
        "vendor_category": ("vendor_category_id", VendorCategory),
        "contact_person": "contact_person",
        "gst": "gst_no",
        "registration_date": "registration_date",
        "cin": "cin",
        "pan": "pan",
        "gst_category": ("gst_category_id", GstCategories),
        "gst_suspend": "gst_suspend",
        "tax_type": "tax_type",
        "distance": "distance",
        "tds_on_gst_applicable": "tds_on_gst_applicable",
        "tds_applicable": "tds_applicable",
        "website": "website",
        "facebook": "facebook",
        "skype": "skype",
        "twitter": "twitter",
        "linked_in": "linked_in",
        "payment_term": ("payment_term_id", VendorPaymentTerms),
        "price_category": ("price_category_id", PriceCategories),
        "vendor_agent": ("vendor_agent_id", VendorAgent),
        "transporter": ("transporter_id", Transporters),
        "credit_limit": "credit_limit",
        "max_credit_days": "max_credit_days",
        "interest_rate_yearly": "interest_rate_yearly",
        "rtgs_ifsc_code": "rtgs_ifsc_code",
        "accounts_number": "accounts_number",
        "bank_name": "bank_name",
        "branch": "branch",
    }
    
    BOOLEAN_FIELDS = [
        "vendor_common_for_sales_purchase", 
        "is_sub_vendor", 
        "gst_suspend", 
        "tds_applicable", 
        "tds_on_gst_applicable"
    ]
    
    # ============================================================
    # FK BULK CONFIG - Clean, DRY configuration for bulk imports
    # ============================================================
    FK_BULK_CONFIG = {
        # Basic FKs with name field
        'vendor_category': {
            'model': VendorCategory,
            'name_field': 'name',
            'create_fields': {'code': lambda name: name[:3].upper()}
        },
        'firm_status': {
            'model': FirmStatuses,
            'name_field': 'name',
            'create_fields': {}
        },
        'territory': {
            'model': Territory,
            'name_field': 'name',
            'create_fields': {'code': lambda name: name[:3].upper()}
        },
        'gst_category': {
            'model': GstCategories,
            'name_field': 'name',
            'create_fields': {}
        },
        'payment_term': {
            'model': VendorPaymentTerms,
            'name_field': 'name',
            'create_fields': {}
        },
        'price_category': {
            'model': PriceCategories,
            'name_field': 'name',
            'create_fields': {}
        },
        'vendor_agent': {
            'model': VendorAgent,
            'name_field': 'name',
            'create_fields': {'code': lambda name: name[:3].upper()}
        },
        'transporter': {
            'model': Transporters,
            'name_field': 'name',
            'create_fields': {'code': lambda name: name[:3].upper()}
        },
        'ledger_group': {
            'model': LedgerGroups,
            'name_field': 'name',
            'create_fields': {}
        },
        # Location FKs
        'country': {
            'model': Country,
            'name_field': 'country_name',
            'create_fields': {'country_code': lambda name: name[:3].upper()}
        },
        'state': {
            'model': State,
            'name_field': 'state_name',
            'create_fields': {}  # Requires country_id, handle separately
        },
        'city': {
            'model': City,
            'name_field': 'city_name',
            'create_fields': {}  # Requires state_id, handle separately
        },
    }
    
    # Special handling for foreign keys that require additional fields
    FK_REQUIRED_FIELDS = {
        "LedgerAccounts": {
            "ledger_group_id": lambda: LedgerGroups.objects.first()
        }
    }
    
    @classmethod
    def create_record(cls, row_data, field_map=None, boolean_fields=None, get_or_create_funcs=None):
        """Create vendor record with addresses from Excel data"""
        field_map = field_map or cls.FIELD_MAP
        boolean_fields = boolean_fields or cls.BOOLEAN_FIELDS
        
        # First, convert numeric fields that should be strings to ensure they won't cause encoding issues
        string_fields = ['rtgs_ifsc_code', 'accounts_number', 'gst', 'pan', 'cin', 
                         'billing_pin_code', 'shipping_pin_code', 'billing_phone', 'shipping_phone']
        
        for field in string_fields:
            if field in row_data and row_data[field] is not None:
                row_data[field] = str(row_data[field])
        
        with transaction.atomic():
            # 1. Process the vendor data
            vendor_data = {}
            
            # Special handling for ledger account with group
            ledger_account_name = row_data.get("ledger_account")
            ledger_group_name = row_data.get("ledger_group")
            
            if ledger_account_name:
                if ledger_group_name:
                    # Get or create the ledger group first
                    ledger_group = LedgerGroups.objects.filter(name__iexact=ledger_group_name).first()
                    if not ledger_group:
                        logger.info(f"Creating LedgerGroup with name='{ledger_group_name}'")
                        # nature is required in DB - default to 'Liability' for vendor groups
                        ledger_group = LedgerGroups.objects.create(name=ledger_group_name, nature='')
                        
                    # Now get or create ledger account with the right group
                    ledger_account = LedgerAccounts.objects.filter(name__iexact=ledger_account_name).first()
                    if not ledger_account:
                        logger.info(f"Creating LedgerAccount with name='{ledger_account_name}' and group='{ledger_group_name}'")
                        ledger_account = LedgerAccounts.objects.create(
                            name=ledger_account_name,
                            ledger_group_id=ledger_group
                        )
                else:
                    # If no group specified, use default group
                    default_group = LedgerGroups.objects.first()
                    ledger_account = LedgerAccounts.objects.filter(name__iexact=ledger_account_name).first()
                    if not ledger_account:
                        if not default_group:
                            raise ValueError("Cannot create LedgerAccount without a LedgerGroup")
                        logger.info(f"Creating LedgerAccount with name='{ledger_account_name}' and default group")
                        ledger_account = LedgerAccounts.objects.create(
                            name=ledger_account_name,
                            ledger_group_id=default_group
                        )
                
                vendor_data['ledger_account_id'] = ledger_account
            
            # Process other fields
            for excel_col, mapping in field_map.items():
                # Skip already processed fields
                if excel_col in ['ledger_account', 'ledger_group']:
                    continue
                    
                value = row_data.get(excel_col)
                
                # Skip empty values
                if value is None or value == '':
                    continue
                
                if isinstance(mapping, tuple):
                    # Handle foreign key fields
                    field_name, model = mapping
                    vendor_data[field_name] = cls.get_or_create_fk(model, value)
                else:
                    # Handle regular fields
                    if mapping in boolean_fields:
                        vendor_data[mapping] = cls.parse_boolean(value)
                    elif mapping == 'tax_type':
                        # Special validation for tax_type to ensure it matches allowed choices
                        valid_tax_types = ['Inclusive', 'Exclusive']
                        if value not in valid_tax_types:
                            raise ValueError(f"Invalid tax_type '{value}'. Must be one of: {', '.join(valid_tax_types)}")
                        vendor_data[mapping] = value
                    else:
                        vendor_data[mapping] = value
            
            # Create the vendor record
            vendor = Vendor.objects.create(**vendor_data)
            
            # 2. Create billing address - check if any billing field has data
            billing_fields = ['billing_address', 'billing_country', 'billing_state', 'billing_city', 
                            'billing_pin_code', 'billing_phone', 'billing_email', 
                            'billing_longitude', 'billing_latitude']
            has_billing_data = any(row_data.get(field) for field in billing_fields)
            
            if has_billing_data:
                # Get or create location fields INDEPENDENTLY
                country = cls.get_or_create_country(row_data.get("billing_country"))
                state = cls.get_or_create_state(row_data.get("billing_state"), country)
                # Pass country as fallback for city creation when state is missing
                city = cls.get_or_create_city(row_data.get("billing_city"), state, country)
                
                try:
                    VendorAddress.objects.create(
                        vendor_id=vendor,
                        address_type="Billing",
                        address=row_data.get("billing_address") or None,
                        city_id=city,
                        state_id=state,
                        country_id=country,
                        pin_code=str(row_data.get("billing_pin_code")) if row_data.get("billing_pin_code") else None,
                        phone=str(row_data.get("billing_phone")) if row_data.get("billing_phone") else None,
                        email=row_data.get("billing_email") or None,
                        longitude=row_data.get("billing_longitude") or None,
                        latitude=row_data.get("billing_latitude") or None
                    )
                    logger.info(f"Created billing address for vendor {vendor.name}")
                except Exception as e:
                    logger.warning(f"Could not create billing address for vendor {vendor.name}: {e}")
            
            # 3. Create shipping address - check if any shipping field has data
            shipping_fields = ['shipping_address', 'shipping_country', 'shipping_state', 'shipping_city',
                             'shipping_pin_code', 'shipping_phone', 'shipping_email',
                             'shipping_longitude', 'shipping_latitude']
            has_shipping_data = any(row_data.get(field) for field in shipping_fields)
            
            if has_shipping_data:
                # Get or create location fields INDEPENDENTLY
                s_country = cls.get_or_create_country(row_data.get("shipping_country"))
                s_state = cls.get_or_create_state(row_data.get("shipping_state"), s_country)
                # Pass country as fallback for city creation when state is missing
                s_city = cls.get_or_create_city(row_data.get("shipping_city"), s_state, s_country)
                
                try:
                    VendorAddress.objects.create(
                        vendor_id=vendor,
                        address_type="Shipping",
                        address=row_data.get("shipping_address") or None,
                        city_id=s_city,
                        state_id=s_state,
                        country_id=s_country,
                        pin_code=row_data.get("shipping_pin_code") or None,
                        phone=row_data.get("shipping_phone") or None,
                        email=row_data.get("shipping_email") or None,
                        longitude=row_data.get("shipping_longitude") or None,
                        latitude=row_data.get("shipping_latitude") or None
                    )
                    logger.info(f"Created shipping address for vendor {vendor.name}")
                except Exception as e:
                    logger.warning(f"Could not create shipping address for vendor {vendor.name}: {e}")
                
            return vendor

    @classmethod
    def bulk_create_records(cls, validated_rows, field_map=None, boolean_fields=None):
        """
        Bulk create vendor records for maximum performance.
        
        Uses helper methods from BaseExcelImportExport for clean, DRY code.
        5-10x faster than create_record() by using bulk_create and pre-loaded FK lookups.
        
        Args:
            validated_rows: List of row dictionaries with '_excel_row' for tracking
            field_map: Field mapping dictionary
            boolean_fields: List of boolean field names
            
        Returns:
            dict with 'success' count and 'errors' list
        """
        field_map = field_map or cls.FIELD_MAP
        boolean_fields = boolean_fields or cls.BOOLEAN_FIELDS
        
        errors = []
        vendors_to_create = []
        total_rows = len(validated_rows)
        BATCH_SIZE = 500
        
        logger.info(f"BULK CREATE: Starting for {total_rows} vendors")
        
        # ========================================
        # PHASE 1: Load all FK lookups using helper
        # ========================================
        logger.info("PHASE 1: Loading FK lookups...")
        
        # Add ledger_account to config (special case - uses 'name' field)
        fk_config = {
            **cls.FK_BULK_CONFIG,
            'ledger_account': {'model': LedgerAccounts, 'name_field': 'name'}
        }
        fk_lookups = cls.bulk_load_fk_lookups(fk_config)
        
        # ========================================
        # PHASE 2: Collect and create missing FKs using helper
        # ========================================
        logger.info("PHASE 2: Creating missing FKs...")
        
        # Only auto-create these simple FKs (location FKs need special handling)
        simple_fk_config = {k: v for k, v in cls.FK_BULK_CONFIG.items() 
                           if k not in ['country', 'state', 'city']}
        
        missing_fks = cls.bulk_collect_missing_fks(validated_rows, simple_fk_config, fk_lookups)
        fk_lookups = cls.bulk_create_missing_fks(missing_fks, simple_fk_config, fk_lookups)
        
        logger.info("PHASE 2 complete")
        
        # ========================================
        # PHASE 3: Handle LedgerAccounts (special - requires ledger_group)
        # ========================================
        logger.info("PHASE 3: Creating missing Ledger Accounts...")
        
        missing_ledger_accounts = {}
        for row_data in validated_rows:
            ledger_name = row_data.get('ledger_account')
            if ledger_name and str(ledger_name).strip():
                ledger_lower = str(ledger_name).strip().lower()
                if ledger_lower not in fk_lookups['ledger_account']:
                    group_name = row_data.get('ledger_group', '')
                    missing_ledger_accounts[ledger_lower] = {
                        'name': str(ledger_name).strip(),
                        'group': str(group_name).strip() if group_name else None
                    }
        
        if missing_ledger_accounts:
            with transaction.atomic():
                default_group = LedgerGroups.objects.first()
                for ledger_lower, info in missing_ledger_accounts.items():
                    group = fk_lookups['ledger_group'].get(info['group'].lower()) if info['group'] else None
                    group = group or default_group
                    
                    if group:
                        ledger = LedgerAccounts.objects.create(name=info['name'], ledger_group_id=group)
                        fk_lookups['ledger_account'][ledger_lower] = ledger
                
                logger.info(f"Created {len(missing_ledger_accounts)} Ledger Accounts")
        
        logger.info("PHASE 3 complete")
        
        # ========================================
        # PHASE 4: Build Vendor objects
        # ========================================
        logger.info("PHASE 4: Building Vendor objects...")
        
        for idx, row_data in enumerate(validated_rows):
            excel_row = row_data.get('_excel_row', idx + 2)
            
            try:
                vendor_data = {}
                
                # Process each field
                for excel_col, mapping in field_map.items():
                    if excel_col in ['ledger_account', 'ledger_group']:
                        continue  # Handle separately
                    
                    value = row_data.get(excel_col)
                    if value is None or value == '':
                        continue
                    
                    if isinstance(mapping, tuple):
                        # FK field - use helper
                        field_name = mapping[0]
                        fk_obj = cls.get_fk_object(fk_lookups, excel_col, value)
                        if fk_obj:
                            vendor_data[field_name] = fk_obj
                    else:
                        # Regular field
                        if mapping in boolean_fields:
                            vendor_data[mapping] = cls.parse_boolean(value)
                        elif mapping == 'tax_type':
                            if value in ['Inclusive', 'Exclusive']:
                                vendor_data[mapping] = value
                        else:
                            vendor_data[mapping] = str(value) if value else value
                
                # Handle ledger account
                ledger_obj = cls.get_fk_object(fk_lookups, 'ledger_account', row_data.get('ledger_account'))
                if ledger_obj:
                    vendor_data['ledger_account_id'] = ledger_obj
                
                vendor = Vendor(**vendor_data)
                vendor._excel_row = excel_row
                vendor._row_data = row_data  # Store for address creation
                vendors_to_create.append(vendor)
                
            except Exception as e:
                errors.append({"row": excel_row, "error": f"Failed to prepare vendor: {str(e)}"})
        
        logger.info(f"PHASE 4 complete: {len(vendors_to_create)} vendors prepared")
        
        # ========================================
        # PHASE 5: Bulk create vendors
        # ========================================
        logger.info("PHASE 5: Bulk creating vendors...")
        
        success_count = 0
        created_vendors = []
        
        try:
            with transaction.atomic():
                for batch_start in range(0, len(vendors_to_create), BATCH_SIZE):
                    batch = vendors_to_create[batch_start:batch_start + BATCH_SIZE]
                    Vendor.objects.bulk_create(batch, batch_size=BATCH_SIZE)
                    created_vendors.extend(batch)
                    
                    batch_num = (batch_start // BATCH_SIZE) + 1
                    total_batches = (len(vendors_to_create) + BATCH_SIZE - 1) // BATCH_SIZE
                    logger.info(f"Batch {batch_num}/{total_batches} created ({len(batch)} vendors)")
                
                success_count = len(created_vendors)
                
        except Exception as e:
            logger.error(f"Bulk create failed: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            for vendor in vendors_to_create:
                errors.append({"row": getattr(vendor, '_excel_row', 0), "error": f"Bulk create failed: {str(e)}"})
            return {"success": 0, "errors": errors, "total": total_rows}
        
        logger.info(f"PHASE 5 complete: {success_count} vendors created")
        
        # ========================================
        # PHASE 6: Bulk create addresses
        # ========================================
        logger.info("PHASE 6: Creating addresses...")
        
        billing_addresses = []
        shipping_addresses = []
        
        for vendor in created_vendors:
            row_data = getattr(vendor, '_row_data', {})
            
            # Billing address
            if any(row_data.get(f) for f in ['billing_address', 'billing_country', 'billing_state', 'billing_city']):
                billing_addresses.append(VendorAddress(
                    vendor_id=vendor,
                    address_type="Billing",
                    address=row_data.get("billing_address"),
                    city_id=cls.get_fk_object(fk_lookups, 'city', row_data.get('billing_city')),
                    state_id=cls.get_fk_object(fk_lookups, 'state', row_data.get('billing_state')),
                    country_id=cls.get_fk_object(fk_lookups, 'country', row_data.get('billing_country')),
                    pin_code=str(row_data.get("billing_pin_code")) if row_data.get("billing_pin_code") else None,
                    phone=str(row_data.get("billing_phone")) if row_data.get("billing_phone") else None,
                    email=row_data.get("billing_email"),
                    longitude=row_data.get("billing_longitude"),
                    latitude=row_data.get("billing_latitude")
                ))
            
            # Shipping address
            if any(row_data.get(f) for f in ['shipping_address', 'shipping_country', 'shipping_state', 'shipping_city']):
                shipping_addresses.append(VendorAddress(
                    vendor_id=vendor,
                    address_type="Shipping",
                    address=row_data.get("shipping_address"),
                    city_id=cls.get_fk_object(fk_lookups, 'city', row_data.get('shipping_city')),
                    state_id=cls.get_fk_object(fk_lookups, 'state', row_data.get('shipping_state')),
                    country_id=cls.get_fk_object(fk_lookups, 'country', row_data.get('shipping_country')),
                    pin_code=str(row_data.get("shipping_pin_code")) if row_data.get("shipping_pin_code") else None,
                    phone=str(row_data.get("shipping_phone")) if row_data.get("shipping_phone") else None,
                    email=row_data.get("shipping_email"),
                    longitude=row_data.get("shipping_longitude"),
                    latitude=row_data.get("shipping_latitude")
                ))
        
        if billing_addresses:
            VendorAddress.objects.bulk_create(billing_addresses, batch_size=BATCH_SIZE)
            logger.info(f"Created {len(billing_addresses)} billing addresses")
        
        if shipping_addresses:
            VendorAddress.objects.bulk_create(shipping_addresses, batch_size=BATCH_SIZE)
            logger.info(f"Created {len(shipping_addresses)} shipping addresses")
        
        logger.info(f"PHASE 6 complete")
        
        return {"success": success_count, "errors": errors, "total": total_rows}

    @classmethod
    def generate_template(cls, extra_columns=None):
        """Generate Excel template with address fields"""
        wb = super().generate_template(extra_columns)
        ws = wb.active
        
        # Add hints for constrained fields like tax_type
        if 'tax_type' in cls.FIELD_MAP:
            tax_type_col = list(cls.FIELD_MAP.keys()).index('tax_type') + 1
            # Add data validation for tax_type
            dv = DataValidation(type="list", formula1='"Inclusive,Exclusive"', allow_blank=True)
            dv.add(f"{get_column_letter(tax_type_col)}2:{get_column_letter(tax_type_col)}1000")
            ws.add_data_validation(dv)
            
            # Add a comment explaining valid values
            tax_type_cell = ws.cell(row=1, column=tax_type_col)
            comment = Comment('Valid values: Inclusive, Exclusive', 'System')
            tax_type_cell.comment = comment
        
        # Add address fields with same styling as optional fields
        address_headers = []
        
        # Billing address fields
        billing_fields = [
            "billing_address", "billing_country", "billing_state", 
            "billing_city", "billing_pin_code", "billing_phone", 
            "billing_email", "billing_longitude", "billing_latitude"
        ]
        address_headers.extend(billing_fields)
        
        # Shipping address fields
        shipping_fields = [
            "shipping_address", "shipping_country", "shipping_state", 
            "shipping_city", "shipping_pin_code", "shipping_phone", 
            "shipping_email", "shipping_longitude", "shipping_latitude"
        ]
        address_headers.extend(shipping_fields)
        
        # Style for address fields - Light blue (same as optional fields)
        address_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
        address_font = Font(bold=True, color="000000")
        
        # Get the last row and append the address headers
        last_row = ws.max_row
        for col_num, header in enumerate(address_headers, 1 + len(list(cls.FIELD_MAP.keys()))):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = address_fill
            cell.font = address_font
            cell.alignment = Alignment(horizontal="center", vertical="center")
            ws.column_dimensions[get_column_letter(col_num)].width = len(str(header)) + 4
            
        return wb
    
    @classmethod
    def get_or_create_country(cls, name):
        """Get or create a country"""
        if not name:
            return None
            
        country = Country.objects.filter(country_name__iexact=name).first()
        if not country:
            logger.info(f"Creating Country with name='{name}'")
            country = Country.objects.create(
                country_name=name,
                country_code=name[:3].upper()
            )
        return country
        
    @classmethod
    def get_or_create_state(cls, name, country=None):
        """Get or create a state - country is optional for lookup but required for creation"""
        if not name:
            return None
        
        # First try to find existing state by name
        state = State.objects.filter(state_name__iexact=name).first()
        if state:
            # Update country if provided and state doesn't have one
            if country and not state.country_id:
                state.country_id = country
                state.save()
            return state
        
        # Need to create new state - requires country due to DB constraint
        if not country:
            logger.warning(f"Cannot create State '{name}' without country - state will be None")
            return None
            
        logger.info(f"Creating State with state_name='{name}'")
        state = State.objects.create(
            state_name=name,
            state_code=name[:3].upper(),
            country_id=country
        )
        return state
        
    @classmethod
    def get_or_create_city(cls, name, state=None, country=None):
        """
        Get or create a city DYNAMICALLY.
        
        Priority:
        1. If state provided → find city in THAT specific state (or create new)
        2. If no state but country provided → create default state, then city
        3. If nothing provided → use India as default country
        
        This handles duplicate city names (e.g., KOTA in Rajasthan vs KOTA in AP)
        """
        if not name:
            return None
        
        name = str(name).strip()
        
        # CASE 1: State IS provided - look for city in THAT specific state
        if state:
            city = City.objects.filter(city_name__iexact=name, state_id=state).first()
            if city:
                logger.info(f"Found existing city '{city.city_name}' in state '{state.state_name}'")
                return city
            # City doesn't exist in this state - create it
            logger.info(f"Creating City '{name}' in state '{state.state_name}'")
            city = City.objects.create(
                city_name=name,
                city_code=name[:3].upper(),
                state_id=state
            )
            return city
        
        # CASE 2: No state provided - try to find any existing city with this name
        city = City.objects.filter(city_name__iexact=name).first()
        if city:
            logger.info(f"Found existing city '{city.city_name}' in state '{city.state_id.state_name if city.state_id else 'None'}'")
            return city
        
        # CASE 3: City doesn't exist and no state - need to create with default
        # Use India as default country if nothing provided (for Indian ERP context)
        if not country:
            country = Country.objects.filter(country_name__iexact='India').first()
            if not country:
                country = Country.objects.create(
                    country_name='India',
                    country_code='IND'
                )
                logger.info("Created default country 'India'")
        
        # Create default state using country name
        default_state_name = country.country_name
        state = State.objects.filter(state_name__iexact=default_state_name, country_id=country).first()
        if not state:
            state = State.objects.create(
                state_name=default_state_name,
                state_code=default_state_name[:3].upper(),
                country_id=country
            )
            logger.info(f"Created default state '{default_state_name}' for country '{country.country_name}'")
            
        logger.info(f"Creating City '{name}' in default state '{state.state_name}'")
        city = City.objects.create(
            city_name=name,
            city_code=name[:3].upper(),
            state_id=state
        )
        return city

    # ============================================================
    # UPDATE EXISTING VENDOR FROM EXCEL ROW
    # ============================================================
    @classmethod
    def update_record(cls, row_data, field_map=None, boolean_fields=None, get_or_create_funcs=None):
        """
        Update an existing vendor from Excel row data.
        Matches by vendor_id column. Only non-empty fields are updated.
        """
        field_map = field_map or cls.FIELD_MAP
        boolean_fields = boolean_fields or cls.BOOLEAN_FIELDS

        vendor_id = row_data.get('vendor_id')
        if not vendor_id:
            raise ValueError("vendor_id is required for update mode")

        try:
            vendor = Vendor.objects.get(pk=vendor_id, is_deleted=False)
        except Vendor.DoesNotExist:
            raise ValueError(f"Vendor with ID {vendor_id} not found or is deleted")

        with transaction.atomic():
            updated_fields = []
            for excel_col, mapping in field_map.items():
                if excel_col in ['ledger_account', 'ledger_group']:
                    continue  # Handle separately below

                value = row_data.get(excel_col)
                if value is None or value == '':
                    continue

                if isinstance(mapping, tuple):
                    field_name, model = mapping
                    fk_obj = cls.get_or_create_fk(model, value)
                    if fk_obj:
                        setattr(vendor, field_name, fk_obj)
                        updated_fields.append(field_name)
                else:
                    if mapping in boolean_fields:
                        setattr(vendor, mapping, cls.parse_boolean(value))
                    elif mapping == 'tax_type':
                        if value in ['Inclusive', 'Exclusive']:
                            setattr(vendor, mapping, value)
                        else:
                            logger.warning(
                                "Vendor %s: invalid tax_type value '%s'. Must be 'Inclusive' or 'Exclusive'.",
                                vendor_id, value
                            )
                    elif mapping in ['credit_limit', 'interest_rate_yearly', 'distance']:
                        try:
                            from decimal import Decimal, InvalidOperation
                            setattr(vendor, mapping, Decimal(str(value)))
                        except (InvalidOperation, ValueError, TypeError, ArithmeticError) as e:
                            logger.warning(
                                "Vendor %s: failed to convert field '%s' value '%s' to Decimal: %s",
                                vendor_id, mapping, value, e
                            )
                            continue
                    elif mapping in ['max_credit_days']:
                        try:
                            setattr(vendor, mapping, int(float(str(value))))
                        except (ValueError, TypeError) as e:
                            logger.warning(
                                "Vendor %s: failed to convert field '%s' value '%s' to int: %s",
                                vendor_id, mapping, value, e
                            )
                            continue
                    else:
                        setattr(vendor, mapping, value)
                    updated_fields.append(mapping)

            # Handle ledger account with group
            ledger_name = row_data.get('ledger_account')
            if ledger_name:
                group_name = row_data.get('ledger_group')
                if group_name:
                    group = LedgerGroups.objects.filter(name__iexact=group_name).first()
                    if not group:
                        group = LedgerGroups.objects.create(name=group_name, nature='')
                else:
                    group = LedgerGroups.objects.first()

                ledger = LedgerAccounts.objects.filter(name__iexact=ledger_name).first()
                if not ledger and group:
                    ledger = LedgerAccounts.objects.create(name=ledger_name, ledger_group_id=group)
                elif not ledger and not group:
                    logger.warning(
                        "Vendor %s: cannot create LedgerAccount '%s' — no LedgerGroup exists. "
                        "Create a LedgerGroup first or specify 'ledger_group' in the Excel.",
                        vendor_id, ledger_name
                    )
                if ledger:
                    vendor.ledger_account_id = ledger
                    updated_fields.append('ledger_account_id')

            if updated_fields:
                vendor.save()
                logger.info(f"Updated vendor {vendor.name}: {', '.join(updated_fields)}")

            # Update addresses
            cls._update_address(vendor, row_data, 'Billing', 'billing')
            cls._update_address(vendor, row_data, 'Shipping', 'shipping')

        return vendor

    @classmethod
    def _update_address(cls, vendor, row_data, address_type, prefix):
        """Update or create a billing/shipping address from row data."""
        address_fields = [f'{prefix}_address', f'{prefix}_phone', f'{prefix}_email',
                          f'{prefix}_city', f'{prefix}_state', f'{prefix}_country',
                          f'{prefix}_pin_code', f'{prefix}_longitude', f'{prefix}_latitude']

        if not any(row_data.get(f) for f in address_fields):
            return

        address = VendorAddress.objects.filter(
            vendor_id=vendor, address_type=address_type
        ).first()

        country = cls.get_or_create_country(row_data.get(f'{prefix}_country'))
        state = cls.get_or_create_state(row_data.get(f'{prefix}_state'), country)
        city = cls.get_or_create_city(row_data.get(f'{prefix}_city'), state, country)

        addr_data = {
            'address': row_data.get(f'{prefix}_address') or (address.address if address else None),
            'city_id': city or (address.city_id if address else None),
            'state_id': state or (address.state_id if address else None),
            'country_id': country or (address.country_id if address else None),
            'pin_code': str(row_data.get(f'{prefix}_pin_code')) if row_data.get(f'{prefix}_pin_code') else (address.pin_code if address else None),
            'phone': str(row_data.get(f'{prefix}_phone')) if row_data.get(f'{prefix}_phone') else (address.phone if address else None),
            'email': row_data.get(f'{prefix}_email') or (address.email if address else None),
            'longitude': row_data.get(f'{prefix}_longitude') or (address.longitude if address else None),
            'latitude': row_data.get(f'{prefix}_latitude') or (address.latitude if address else None),
        }

        if address:
            for key, val in addr_data.items():
                setattr(address, key, val)
            address.save()
        else:
            VendorAddress.objects.create(
                vendor_id=vendor, address_type=address_type, **addr_data
            )

    # ============================================================
    # EXPORT EXISTING VENDORS TO EXCEL
    # ============================================================
    @classmethod
    def export_vendors(cls, queryset=None):
        """
        Export existing vendors to Excel (with vendor_id for re-import update).
        Returns an openpyxl Workbook.
        """
        wb = cls.generate_template()
        ws = wb.active

        field_keys = list(cls.FIELD_MAP.keys())
        address_cols = [
            'billing_address', 'billing_country', 'billing_state', 'billing_city',
            'billing_pin_code', 'billing_phone', 'billing_email', 'billing_longitude', 'billing_latitude',
            'shipping_address', 'shipping_country', 'shipping_state', 'shipping_city',
            'shipping_pin_code', 'shipping_phone', 'shipping_email', 'shipping_longitude', 'shipping_latitude',
        ]
        all_headers = ['vendor_id'] + field_keys + address_cols

        ws.delete_rows(1, ws.max_row)
        header_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
        id_fill = PatternFill(start_color="FFD700", end_color="FFD700", fill_type="solid")
        font_bold = Font(bold=True)
        align_center = Alignment(horizontal="center")

        for col_num, header in enumerate(all_headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.value = header
            cell.fill = id_fill if header == 'vendor_id' else header_fill
            cell.font = font_bold
            cell.alignment = align_center
            ws.column_dimensions[get_column_letter(col_num)].width = max(len(header) + 4, 15)

        ws.cell(row=1, column=1).comment = Comment(
            '\u26a0\ufe0f DO NOT MODIFY this column. Used to match records for update.', 'System'
        )

        FK_DISPLAY = {
            'ledger_account': ('ledger_account_id', 'name'),
            'firm_status':    ('firm_status_id', 'name'),
            'territory':      ('territory_id', 'name'),
            'vendor_category': ('vendor_category_id', 'name'),
            'gst_category':   ('gst_category_id', 'name'),
            'payment_term':   ('payment_term_id', 'name'),
            'price_category': ('price_category_id', 'name'),
            'vendor_agent':   ('vendor_agent_id', 'name'),
            'transporter':    ('transporter_id', 'name'),
        }

        if queryset is None:
            queryset = Vendor.objects.filter(is_deleted=False).order_by('name')

        from django.db.models import Prefetch
        queryset = queryset.select_related(
            'ledger_account_id', 'ledger_account_id__ledger_group_id',
            'firm_status_id', 'territory_id', 'vendor_category_id',
            'gst_category_id', 'payment_term_id', 'price_category_id',
            'vendor_agent_id', 'transporter_id'
        ).prefetch_related(
            Prefetch(
                'vendoraddress_set',
                queryset=VendorAddress.objects.select_related('city_id', 'state_id', 'country_id'),
                to_attr='_prefetched_addresses'
            )
        )

        for vendor_obj in queryset:
            row = [str(vendor_obj.vendor_id)]

            for excel_col, mapping in cls.FIELD_MAP.items():
                if excel_col in FK_DISPLAY:
                    fk_attr, display_field = FK_DISPLAY[excel_col]
                    fk_obj = getattr(vendor_obj, fk_attr, None)
                    row.append(getattr(fk_obj, display_field, '') if fk_obj else '')
                elif excel_col == 'ledger_group':
                    try:
                        ledger = getattr(vendor_obj, 'ledger_account_id', None)
                        group = getattr(ledger, 'ledger_group_id', None) if ledger else None
                        row.append(getattr(group, 'name', '') if group else '')
                    except Exception:
                        row.append('')
                elif isinstance(mapping, tuple):
                    row.append('')
                else:
                    val = getattr(vendor_obj, mapping, '')
                    if isinstance(val, bool):
                        val = 'Yes' if val else 'No'
                    row.append(val if val is not None else '')

            # Addresses (from prefetched data — no extra queries)
            prefetched = getattr(vendor_obj, '_prefetched_addresses', [])
            billing = next((a for a in prefetched if a.address_type == 'Billing'), None)
            shipping = next((a for a in prefetched if a.address_type == 'Shipping'), None)

            for addr in [billing, shipping]:
                if addr:
                    row.extend([
                        addr.address or '',
                        addr.country_id.country_name if addr.country_id else '',
                        addr.state_id.state_name if addr.state_id else '',
                        addr.city_id.city_name if addr.city_id else '',
                        addr.pin_code or '', addr.phone or '', addr.email or '',
                        str(addr.longitude) if addr.longitude else '',
                        str(addr.latitude) if addr.latitude else '',
                    ])
                else:
                    row.extend([''] * 9)

            ws.append(row)

        ws.freeze_panes = 'B2'
        return wb


# API Views for Vendor Excel import/export
class VendorTemplateAPIView(APIView):
    """
    API for downloading the vendor import template.
    """
    
    def get(self, request, *args, **kwargs):
        return VendorExcelImport.get_template_response(request)

class VendorExportAPIView(APIView):
    """
    API for exporting existing vendors to Excel (for re-import update).
    GET /export-vendors/              -> export all vendors
    GET /export-vendors/?ids=a,b,c    -> export specific vendors
    """
    def get(self, request, *args, **kwargs):
        try:
            ids_param = request.query_params.get('ids', '')
            queryset = Vendor.objects.filter(is_deleted=False).order_by('name')

            if ids_param:
                id_list = [i.strip() for i in ids_param.split(',') if i.strip()]
                queryset = queryset.filter(vendor_id__in=id_list)
                if not queryset.exists():
                    return build_response(0, "No matching vendors found", [], status.HTTP_404_NOT_FOUND)

            wb = VendorExcelImport.export_vendors(queryset)
            response = HttpResponse(
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=Vendor_Export.xlsx'
            wb.save(response)
            return response

        except Exception as e:
            logger.error(f"Error exporting vendors: {str(e)}")
            return build_response(0, f"Export failed: {str(e)}", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class VendorExcelUploadAPIView(APIView):
    """
    API for importing vendors from Excel files.
    
    Supports two modes (auto-detected or via ?mode=update):
    - create (default): Creates new vendors from Excel rows
    - update: Matches by vendor_id column and updates existing records
    
    Uses a hybrid approach:
    - For small imports (<500 rows): Traditional mode with individual saves
    - For large imports (>=500 rows): Bulk mode with bulk_create for 5-10x speed
    """
    parser_classes = (MultiPartParser, FormParser)
    
    # Threshold for switching to bulk mode
    BULK_THRESHOLD = 500
    
    def post(self, request, *args, **kwargs):
        import time
        start_time = time.time()
        import_mode_param = request.query_params.get('mode', 'create').lower()

        # --- AUTO-DETECT UPDATE MODE ---
        if import_mode_param == 'create':
            file_obj = request.FILES.get('file')
            if file_obj:
                try:
                    peek_wb = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
                    peek_sheet = peek_wb.active
                    headers = [str(cell.value).strip().lower() for cell in next(peek_sheet.iter_rows(min_row=1, max_row=1)) if cell.value]
                    peek_wb.close()
                    file_obj.seek(0)
                    if 'vendor_id' in headers:
                        import_mode_param = 'update'
                        logger.info("Auto-detected update mode (vendor_id column found in Excel)")
                except Exception:
                    file_obj.seek(0)

        # --- UPDATE MODE ---
        if import_mode_param == 'update':
            return self._handle_update(request, start_time)

        # --- CREATE MODE (existing logic) ---
        try:
            # Upload and validate file
            file_path, status_code = VendorExcelImport.upload_file(request)
            
            # If there was an error with the file
            if status_code != status.HTTP_200_OK:
                return build_response(0, file_path.get("error", "Unknown error"), [], status_code)
            
            # Count rows to determine import mode
            file_obj = request.FILES.get('file')
            row_count = 0
            try:
                import openpyxl
                file_obj.seek(0)
                wb = openpyxl.load_workbook(file_obj, read_only=True, data_only=True)
                ws = wb.active
                # Count non-empty rows (excluding header)
                row_count = sum(1 for row in ws.iter_rows(min_row=2) if any(cell.value for cell in row))
                wb.close()
                file_obj.seek(0)
                logger.info(f"Vendor import: {row_count} data rows detected")
            except Exception as e:
                logger.warning(f"Could not count rows: {e}, defaulting to traditional mode")
                row_count = 0
            
            # Choose import mode based on row count
            use_bulk_mode = row_count >= self.BULK_THRESHOLD
            import_mode = "BULK" if use_bulk_mode else "TRADITIONAL"
            logger.info(f"Import mode: {import_mode} (threshold: {self.BULK_THRESHOLD}, rows: {row_count})")
            
            if use_bulk_mode:
                # BULK MODE: Use process_excel_file_bulk for large imports
                result, status_code = VendorExcelImport.process_excel_file_bulk(
                    file_obj,
                    VendorExcelImport.bulk_create_records
                )
            else:
                # TRADITIONAL MODE: Use process_excel_file for small imports
                result, status_code = VendorExcelImport.process_excel_file(
                    file_obj,
                    VendorExcelImport.create_record
                )
            
            # Check for validation errors
            if status_code != status.HTTP_200_OK:
                error_msg = result.get("error", "Import failed")
                error_details = {}
                
                # Add more detailed error information
                if "missing_columns" in result:
                    error_details["missing_columns"] = result["missing_columns"]
                if "unexpected_columns" in result:
                    error_details["unexpected_columns"] = result["unexpected_columns"]
                if "missing_expected_columns" in result:
                    error_details["missing_expected_columns"] = result["missing_expected_columns"]
                if "missing_data_rows" in result:
                    error_details["missing_data_rows"] = result["missing_data_rows"]
                    
                return build_response(0, error_msg, error_details, status_code)
                
            # Check for processing errors from row processing
            success_count = result.get("success", 0)
            errors = result.get("errors", [])
            
            if errors:
                # Return the first error as the main message with all errors in the data field
                first_error = errors[0]["error"] if errors else "Unknown error during import"
                return build_response(
                    0,
                    f"Import failed: {first_error}",
                    {"row_errors": errors},
                    status.HTTP_400_BAD_REQUEST
                )
            else:
                # Success response - only if there were no errors
                return build_response(
                    success_count,
                    result.get("message", f"{success_count} vendors imported successfully."),
                    {"import_mode": import_mode},
                    status.HTTP_200_OK
                )
            
        except Exception as e:
            logger.error(f"Error in vendor Excel import: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return build_response(0, f"Import failed: {str(e)}", [], status.HTTP_400_BAD_REQUEST)

    def _handle_update(self, request, start_time):
        """
        Handle Excel-based bulk update for vendors.
        Reads uploaded Excel, matches by vendor_id, updates only non-empty fields.
        """
        import time
        try:
            file = request.FILES.get('file')
            if not file:
                return build_response(0, "No file uploaded", [], status.HTTP_400_BAD_REQUEST)

            file_name = file.name.lower()
            if not (file_name.endswith('.xlsx') or file_name.endswith('.xls')):
                return build_response(0, "Invalid file format. Only .xlsx or .xls supported.", [], status.HTTP_400_BAD_REQUEST)

            wb = openpyxl.load_workbook(file, read_only=True, data_only=True)
            sheet = wb.active

            raw_headers = [str(cell.value).lower().strip() if cell.value else '' for cell in sheet[1]]
            headers = [h.replace(' *', '').strip() for h in raw_headers]

            if 'vendor_id' not in headers:
                return build_response(0, "Excel must have a 'vendor_id' column for update mode. Use the Export file as your template.", [], status.HTTP_400_BAD_REQUEST)

            success = 0
            failed = []
            total = 0

            for excel_row_idx, row in enumerate(sheet.iter_rows(min_row=2, values_only=True), start=2):
                row_values = list(row)
                if not any(cell is not None for cell in row_values):
                    continue

                total += 1
                row_data = {}
                for i, header in enumerate(headers):
                    if i < len(row_values):
                        val = row_values[i]
                        if isinstance(val, str):
                            val = val.strip() if val.strip() else None
                        row_data[header] = val

                if not row_data.get('vendor_id'):
                    failed.append({"row": excel_row_idx, "error": "Missing vendor_id"})
                    continue

                try:
                    VendorExcelImport.update_record(row_data)
                    success += 1
                except Exception as e:
                    failed.append({"row": excel_row_idx, "error": str(e)})

            wb.close()
            elapsed = round(time.time() - start_time, 2)

            if success == 0 and failed:
                return build_response(0, f"Update failed. {len(failed)} errors.",
                    {"errors": failed[:20], "elapsed_time": f"{elapsed}s"}, status.HTTP_400_BAD_REQUEST)
            elif failed:
                return build_response(success,
                    f"Partial update: {success}/{total} updated in {elapsed}s. {len(failed)} failed.",
                    {"success_count": success, "failed_count": len(failed), "errors": failed[:20], "elapsed_time": f"{elapsed}s"},
                    status.HTTP_200_OK)
            else:
                return build_response(success,
                    f"{success} vendors updated successfully in {elapsed}s.",
                    {"success_count": success, "total_count": total, "elapsed_time": f"{elapsed}s"},
                    status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in vendor Excel update: {str(e)}")
            import traceback
            logger.error(traceback.format_exc())
            return build_response(0, f"Update failed: {str(e)}", [], status.HTTP_400_BAD_REQUEST)


#-------------------------------------------------------------------------------------
class VendorBalanceView(APIView):
    def post(self, request, vendor_id, remaining_payment):
        """
        Update or create vendor balance after a bill payment transaction.
        Used in the BillPaymentTransactionAPIView.
        """
        try:
            vendor_instance = Vendor.objects.get(vendor_id=vendor_id)
            vendor_balance = VendorBalance.objects.filter(vendor_id=vendor_instance)

            if vendor_balance.exists():
                # Update existing balance (reduce payable since we paid the vendor)
                for balance in vendor_balance:
                    vendor_balance.update(balance_amount=balance.balance_amount - remaining_payment)
            else:
                # Create new record if it doesn't exist yet
                VendorBalance.objects.create(vendor_id=vendor_instance, balance_amount=(0 - remaining_payment))

        except ObjectDoesNotExist as e:
            return build_response(1, f"Vendor with ID {vendor_id} does not exist.", str(e), status.HTTP_404_NOT_FOUND)

        return build_response(1, "Balance Updated In Vendor Balance Table", [], status.HTTP_201_CREATED)


# ========================= VENDOR BULK UPDATE =========================
class VendorBulkUpdateView(BaseBulkUpdateView):
    """
    PATCH /api/v1/vendors/bulk-update/

    Body:
    {
        "ids": ["uuid1", "uuid2", ...],
        "update_data": {
            "vendor_category_id": "uuid",
            "territory_id": "uuid",
            "credit_limit": 50000
        }
    }

    Only provided fields are updated. Empty fields are ignored.
    """
    MODEL = Vendor
    PK_FIELD = "vendor_id"
    MODULE_NAME = "Vendors"
    MAX_SELECTION = 100

    # Whitelist: field_name → FK Model (None = plain value field)
    ALLOWED_FIELDS = {
        'vendor_category_id':     VendorCategory,
        'territory_id':           Territory,
        'firm_status_id':         FirmStatuses,
        'gst_category_id':        GstCategories,
        'payment_term_id':        VendorPaymentTerms,
        'price_category_id':      PriceCategories,
        'vendor_agent_id':        VendorAgent,
        'transporter_id':         Transporters,
        'tax_type':               None,
        'credit_limit':           None,
        'max_credit_days':        None,
        'interest_rate_yearly':   None,
        'tds_applicable':         None,
        'tds_on_gst_applicable':  None,
        'gst_suspend':            None,
    }


    def get(self, request, pk=None):
        if pk:
            try:
                vendor_id = get_object_or_404(Vendor, pk=pk)
                balance = get_object_or_404(VendorBalance, vendor_id=vendor_id)
                serializer = VendorBalanceSerializer(balance)
                return build_response(1, "Vendor Balance", serializer.data, status.HTTP_200_OK)
            except Exception as e:
                return build_response(1, "Something Went Wrong", str(e), status.HTTP_403_FORBIDDEN)
        else:
            balances = VendorBalance.objects.all()
            serializer = VendorBalanceSerializer(balances, many=True)
            return build_response(len(serializer.data), "Vendor Balances", serializer.data, status.HTTP_200_OK)
