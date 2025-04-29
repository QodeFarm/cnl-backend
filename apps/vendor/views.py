import logging
from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import render,get_object_or_404
from django.http import  Http404
from requests import Response
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError

from apps.customfields.models import CustomFieldValue
from apps.customfields.serializers import CustomFieldValueSerializer
from apps.vendor.filters import VendorAgentFilter, VendorCategoryFilter, VendorFilter, VendorPaymentTermsFilter
from config.utils_filter_methods import filter_response, list_filtered_objects
from .models import Vendor, VendorCategory, VendorPaymentTerms, VendorAgent, VendorAttachment, VendorAddress
from .serializers import VendorSerializer, VendorCategorySerializer, VendorPaymentTermsSerializer, VendorAgentSerializer, VendorAttachmentSerializer, VendorAddressSerializer, VendorSummaryReportSerializer, VendorsOptionsSerializer
from config.utils_methods import delete_multi_instance, list_all_objects, create_instance, update_instance, build_response, validate_input_pk, validate_payload_data, validate_multiple_data, generic_data_creation, validate_put_method_data, update_multi_instances
from uuid import UUID
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter

from django.http import HttpResponseRedirect
from urllib.parse import urlencode

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.

class VendorsView(viewsets.ModelViewSet):
    queryset = Vendor.objects.all().order_by('-created_at')	
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
    queryset = VendorCategory.objects.all().order_by('-created_at')	
    serializer_class = VendorCategorySerializer 
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = VendorCategoryFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, VendorCategory,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class VendorPaymentTermsView(viewsets.ModelViewSet):
    queryset = VendorPaymentTerms.objects.all().order_by('-created_at')	
    serializer_class = VendorPaymentTermsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = VendorPaymentTermsFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, VendorPaymentTerms,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)    

class VendorAgentView(viewsets.ModelViewSet):
    queryset = VendorAgent.objects.all().order_by('-created_at')	
    serializer_class = VendorAgentSerializer   
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = VendorAgentFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, VendorAgent,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

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
        queryset = Vendor.objects.all().order_by('-created_at')
        queryset, total_count = self.apply_filters(request, queryset, VendorFilter, Vendor)

        serializer = VendorsOptionsSerializer(queryset, many=True)
        return filter_response(queryset.count(), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

    def get_vendors(self, request):
        """Applies filters, pagination, and retrieves vendor data."""
        logger.info("Retrieving all vendors")

        page, limit = self.get_pagination_params(request)
        queryset = Vendor.objects.all().order_by('-created_at')
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
            instance.delete()

            logger.info(f"Vendor with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except Vendor.DoesNotExist:
            logger.warning(f"Vendor with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting Vendor with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)


