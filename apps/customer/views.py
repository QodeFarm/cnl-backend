from uuid import UUID
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from requests import request
from rest_framework import viewsets, generics, mixins as mi
from apps import customer
from apps.customer.filters import CustomerCreditLimitReportFilter, CustomerOrderHistoryReportFilter, CustomerSummaryReportFilter, LedgerAccountsFilters, CustomerFilters, CustomerAddressesFilters, CustomerAttachmentsFilters, CustomerLedgerReportFilter, CustomerOutstandingReportFilter
from apps.customfields.models import CustomField, CustomFieldValue
from apps.customfields.serializers import CustomFieldSerializer, CustomFieldValueSerializer
from apps.sales.filters import SaleOrderFilter
from apps.sales.models import SaleInvoiceOrders, SaleOrder
from config.utils_db_router import set_db
from config.utils_filter_methods import filter_response, list_filtered_objects
from .models import *
from .serializers import *
from apps.company.models import Companies
from config.utils_methods import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
import logging
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError
from django.core.exceptions import  ObjectDoesNotExist
from django.db.models import Sum, F, DecimalField, ExpressionWrapper,When,Value,Case,FloatField,Max
from django.db.models.functions import Coalesce

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__) 

# Create your views here.

class LedgerAccountsViews(viewsets.ModelViewSet):
    queryset = LedgerAccounts.objects.all().order_by('-created_at')
    serializer_class = LedgerAccountsSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = LedgerAccountsFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, LedgerAccounts, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class CustomerViews(viewsets.ModelViewSet):
    queryset = Customer.objects.all().order_by('-created_at')	
    serializer_class = CustomerSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CustomerFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        # return create_instance(self, request, *args, **kwargs)
        summary = request.query_params.get('summary', 'false').lower() == 'true'
        if summary:
            customers = self.filter_queryset(self.get_queryset())
            data = CustomerOptionSerializer.get_customer_summary(customers)
            
            Result = Response(data, status=status.HTTP_200_OK)
        else:
            Result = list_all_objects(self, request, *args, **kwargs)
        
        return Result

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    
class CustomerAddressesViews(viewsets.ModelViewSet):
    queryset = CustomerAddresses.objects.all()
    serializer_class = CustomerAddressesSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CustomerAddressesFilters 
    ordering_fields = ['created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class CustomerAttachmentsViews(viewsets.ModelViewSet):
    queryset = CustomerAttachments.objects.all()
    serializer_class = CustomerAttachmentsSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CustomerAttachmentsFilters 
    ordering_fields = ['attachment_name', 'created_at', 'updated_at']
    
    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

#==========================================================================  
    
class CustomerCreateViews(APIView):
    def get_object(self, pk):
        try:
            return Customer.objects.get(pk=pk)
        except Customer.DoesNotExist:
            logger.warning(f"Customer with ID {pk} does not exist.")
            return None

    def get(self, request, *args, **kwargs):
        """Handles GET requests to retrieve customers with optional filters and reports."""
        try:
            if "pk" in kwargs:
                result = validate_input_pk(self, kwargs['pk'])
                return result if result else self.retrieve(self, request, *args, **kwargs)

            if request.query_params.get("summary", "false").lower() == "true":
                return self.get_customer_summary(request)
            
            if request.query_params.get("customer_summary_report", "false").lower() == "true":
                return self.get_customer_summary_report(request)
            
            if request.query_params.get("customer_ledger_report", "false").lower() == "true":
                return self.get_customer_ledger_report(request)
            
            if request.query_params.get("customer_outstanding_report", "false").lower() == "true":
                return self.get_customer_outstanding_report(request)
            
            if request.query_params.get("customer_order_history", "false").lower() == "true":
             return self.get_customer_order_history(request)
         
            if request.query_params.get("credit_limit_report", "false").lower() == "true":
             return self.get_customer_credit_limit_report(request)
            
            if request.query_params.get("customer_payment_report", "false").lower() == "true":
             return self.get_customer_payment_report(request)
         
            return self.get_customers(request)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_pagination_params(self, request):
        """Extracts pagination parameters from the request."""
        page = int(request.query_params.get('page', 1))
        limit = int(request.query_params.get('limit', 10))
        return page, limit
    
    def get_customers(self, request):
        """Applies filters, pagination, and retrieves customers."""
        logger.info("Retrieving all customers")

        page, limit = self.get_pagination_params(request)
        using_db = self.resolve_db_from_request(request)

        queryset = Customer.objects.using(using_db).all().order_by('-created_at')

        if request.query_params:
            filterset = CustomerFilters(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = Customer.objects.using(using_db).count()
        serializer = CustomerSerializer(queryset, many=True)

        return filter_response(queryset.count(), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)


    def get_customer_summary(self, request):
        """Fetches customer summary data."""
        logger.info("Retrieving customer summary")

        page, limit = self.get_pagination_params(request)
        # using_db = self.resolve_db_from_request(request)

        queryset = Customer.objects.all().order_by('-created_at')

        if request.query_params:
            filterset = CustomerFilters(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = Customer.objects.count()
        serializer = CustomerOptionSerializer(queryset, many=True)

        return filter_response(queryset.count(), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

    # def resolve_db_from_request(self, request):
    #     """
    #     Determines the DB to use:
    #     - If `sale_type=Other` --> use 'mstcnl'
    #     - If `bill_type=Others` --> use 'mstcnl' 
    #     - Else → use 'default'
    #     """
    #     bill_type = request.query_params.get("bill_type")
    #     sale_type = request.query_params.get("sale_type")

    #     if (bill_type and bill_type.lower() == 'others') or (sale_type and sale_type.lower() == 'other'):
    #         return 'mstcnl'

    #     return 'default'

    def get_customer_summary_report(self, request):
        """Fetches a summary report of total sales and outstanding payments per customer."""
        logger.info("Retrieving customer summary report data")
        page, limit = self.get_pagination_params(request)
        
       # Annotate each customer with aggregated values.
        queryset = Customer.objects.annotate(
            total_sales=Sum('saleorder__item_value', output_field=DecimalField(max_digits=18, decimal_places=2)),
            total_advance=Sum('saleorder__advance_amount', output_field=DecimalField(max_digits=18, decimal_places=2)),
            outstanding_payments=Sum(
                ExpressionWrapper(
                    F('saleorder__item_value') - F('saleorder__advance_amount'),
                    output_field=DecimalField(max_digits=18, decimal_places=2)
                )
            )
        ).order_by('name')
        if request.query_params:
            filterset = CustomerSummaryReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
                
        total_count = Customer.objects.count()
        serializer = CustomerSummaryReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    
    def get_customer_order_history(self, request):
        """Fetches past purchases by customers."""
        logger.info("Retrieving customer order history report data")

        page, limit = self.get_pagination_params(request)

         # Retrieve all sale invoice orders (sorted by invoice_date descending)
        queryset = SaleInvoiceOrders.objects.all().order_by('-invoice_date')
        
        if request.query_params:
            filterset = CustomerOrderHistoryReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
                
        total_count = SaleInvoiceOrders.objects.count()        
        serializer = CustomerOrderHistoryReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    def get_customer_credit_limit_report(self, request):
        """Fetches assigned credit limits vs. usage per customer."""
        logger.info("Retrieving customer credit limit report data")

        page, limit = self.get_pagination_params(request)
        queryset = Customer.objects.annotate(
            credit_usage=Coalesce(
                Sum(
                    ExpressionWrapper(
                        F('saleinvoiceorders__total_amount') - F('saleinvoiceorders__advance_amount'),
                        output_field=DecimalField(max_digits=18, decimal_places=2)
                    )
                ),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))
            )
        ).annotate(
            remaining_credit=ExpressionWrapper(
                Coalesce(F('credit_limit'), Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))) - F('credit_usage'),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            )
        ).order_by('name')
        # total_count = queryset.count()
        if request.query_params:
            filterset = CustomerCreditLimitReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
                
        total_count = Customer.objects.count()
        serializer = CustomerCreditLimitReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
    
    def get_customer_ledger_report(self, request):
        """Fetches all financial transactions with a specific customer and calculates running balance."""
        logger.info("Retrieving customer ledger report data")
        page, limit = self.get_pagination_params(request)
        
        from apps.finance.models import JournalEntryLines
        
        # Get customer_id filter from request params if provided
        customer_id = request.query_params.get('customer_id')
        
        # Start with base queryset filtering only for entries related to customers
        queryset = JournalEntryLines.objects.filter(customer_id__isnull=False).select_related(
            'journal_entry_id', 'customer_id'
        ).order_by('journal_entry_id__entry_date')
        
        # Apply customer filter if provided
        if customer_id:
            queryset = queryset.filter(customer_id=customer_id)
            
        # Apply filters from request
        if request.query_params:
            filterset = CustomerLedgerReportFilter(request.GET, queryset=queryset)
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
            # For customer ledger: debit increases balance, credit decreases
            running_balance += record.debit - record.credit
            record.running_balance = running_balance
        
        # Apply pagination manually after calculating running balance
        if page and limit:
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            records = records[start_idx:end_idx]
        
        # Serialize the data with the running balance included
        serializer = CustomerLedgerReportSerializer(records, many=True)
        return filter_response(len(records), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)
    
    def get_customer_outstanding_report(self, request):
        """
        Fetches a simplified report of pending payments per customer.
        """
        logger.info("Retrieving simplified customer outstanding report")
        page, limit = self.get_pagination_params(request)
        
        from django.utils import timezone
        from django.db.models import Sum, F, DecimalField, Value, ExpressionWrapper
        from django.db.models.functions import Coalesce
        
        # Start with a base queryset of customers
        queryset = Customer.objects.all()
        
        # Calculate total sales and payments
        customers = queryset.annotate(
            # Total sales (invoiced amount)
            total_sales=Coalesce(
                Sum('saleinvoiceorders__total_amount', output_field=DecimalField(max_digits=18, decimal_places=2)),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))
            ),
            # Total payments received
            total_paid=Coalesce(
                Sum('saleinvoiceorders__advance_amount', output_field=DecimalField(max_digits=18, decimal_places=2)),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))
            ),
            # Get the most recent payment date
            last_payment_date=Max('saleinvoiceorders__due_date')
        )
        
        # Calculate total pending amount
        customers = customers.annotate(
            total_pending=ExpressionWrapper(
                F('total_sales') - F('total_paid'),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            )
        )
        
        # Filter out customers with no outstanding payments
        customers = customers.filter(total_pending__gt=0).order_by('-total_pending')
        
        # Apply any additional filters from the request
        if request.query_params:
            filterset = CustomerOutstandingReportFilter(request.GET, queryset=customers)
            if filterset.is_valid():
                customers = filterset.qs
        
        total_count = customers.count()
        
        serializer = CustomerOutstandingReportSerializer(customers, many=True)
        return filter_response(customers.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK )
    
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a sale order and its related data (items, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the SaleOrder instance
            customer_data = get_object_or_404(Customer, pk=pk)
            customer_serializer = CustomerSerializer(customer_data)

            # Retrieve related data
            attachments_data = self.get_related_data(CustomerAttachments, CustomerAttachmentsSerializers, 'customer_id', pk)
            addresses_data = self.get_related_data(CustomerAddresses, CustomerAddressesSerializers, 'customer_id', pk)
            
            # Retrieve custom field values
            custom_field_values_data = self.get_related_data(CustomFieldValue, CustomFieldValueSerializer, 'custom_id', pk)


            # Customizing the response data
            custom_data = {
                "customer_data": customer_serializer.data,
                "customer_attachments": attachments_data,
                "customer_addresses": addresses_data,
                "custom_field_values": custom_field_values_data  # Add custom field values
            }
            logger.info("Customers and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK) 

        except Http404:
            logger.error("Sale order with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving sale order with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug(
                f"Retrieved related data for model {model.__name__} with filter {filter_field}={filter_value}."
            )
            return serializer.data
        except Exception as e:
            logger.exception(
                f"Error retrieving related data for model {model.__name__} with filter {filter_field}={filter_value}: {str(e)}"
            )
            return []
      
    # @transaction.atomic
    # def delete(self, request, pk, *args, **kwargs):
    #     """
    #     Handles the deletion of a sale order and its related attachments and shipments.
    #     """
    #     try:
    #         # Get the Customer instance
    #         instance = Customer.objects.get(pk=pk)
    #         update_field = {'custom_id': 'customer_id'}
    #         # Delete related CustomerAttachments and CustomerAddresses
    #         if not delete_multi_instance(pk, Customer, CustomerAttachments, main_model_field_name='customer_id'):
    #             return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         if not delete_multi_instance(pk, Customer, CustomerAddresses, main_model_field_name='customer_id'):
    #             return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    #         if not delete_multi_instance(pk, Customer, CustomFieldValue, main_model_field_name='custom_id'):
    #             return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    #         # Delete from mstcnl DB
    #         try:
    #             mst_customer = CustomersMstModel.objects.using('mstcnl').filter(customer_id=pk).first()
    #             if mst_customer:
    #                 mst_customer.delete(using='mstcnl')
    #                 logger.info(f"Customer with ID {pk} deleted from mstcnl database.")
    #             else:
    #                 logger.warning(f"No mstcnl customer found with ID {pk}.")
    #         except Exception as mstcnl_error:
    #             logger.error(f"Error deleting mstcnl customer with ID {pk}: {str(mstcnl_error)}")
    #             return build_response(0, "Error deleting record from mstcnl database", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    #         # Delete the main Customer instance
    #         instance.delete()

    #         logger.info(f"Customer with ID {pk} deleted successfully.")
    #         return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
    #     except Customer.DoesNotExist:
    #         logger.warning(f"Customer with ID {pk} does not exist.")
    #         return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
    #     except Exception as e:
    #         logger.error(f"Error deleting Customer with ID {pk}: {str(e)}")
    #         return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Soft-delete the Customer and cleanup related child objects.
        """
        try:
            # Get the Customer instance
            instance = Customer.objects.get(pk=pk)

            # Delete related CustomerAttachments, CustomerAddresses, etc.
            if not delete_multi_instance(pk, Customer, CustomerAttachments, main_model_field_name='customer_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, Customer, CustomerAddresses, main_model_field_name='customer_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, Customer, CustomFieldValue, main_model_field_name='custom_id'):
                return build_response(0, "Error deleting related custom fields", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete from mstcnl DB (optional: you may soft delete here too)
            try:
                mst_customer = CustomersMstModel.objects.using('mstcnl').filter(customer_id=pk).first()
                if mst_customer:
                    # 👉 Soft delete here too if needed:
                    mst_customer.is_deleted = True
                    mst_customer.save(using='mstcnl')
                    logger.info(f"Customer with ID {pk} soft-deleted in mstcnl database.")
                else:
                    logger.warning(f"No mstcnl customer found with ID {pk}.")
            except Exception as mstcnl_error:
                logger.error(f"Error deleting mstcnl customer with ID {pk}: {str(mstcnl_error)}")
                return build_response(0, "Error deleting record from mstcnl database", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # 🔑 👉 Instead of real delete:
            instance.is_deleted = True
            instance.save()

            logger.info(f"Customer with ID {pk} marked as is_deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)

        except Customer.DoesNotExist:
            logger.warning(f"Customer with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting Customer with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    # Handling POST requests for creating
    def post(self, request, *args, **kwargs):   #To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
        return self.create(request, *args, **kwargs)
    
    # def create(self, request, *args, **kwargs):
    #     given_data = request.data
    #     print("Given data:", given_data)
    #     # db_name = set_db('default')
        
    #     # print("Db name : ", db_name)
    #     # Extract customer_data from the request
    #     customer_data = given_data.pop('customer_data', None)

    #     # Validate customer_data
    #     if customer_data:
    #         # Check if 'picture' exists in customer_data and is a list
    #         picture_data = customer_data.get('picture', None)
    #         if picture_data:
    #             if not isinstance(picture_data, list):
    #                 return build_response(0, "'picture' field in customer_data must be a list.", [], status.HTTP_400_BAD_REQUEST)

    #             for attachment in picture_data:
    #                 if not all(key in attachment for key in ['uid', 'name', 'attachment_name', 'file_size', 'attachment_path']):
    #                     return build_response(0, "Missing required fields in some picture data.", [], status.HTTP_400_BAD_REQUEST)
            
    #         # Validate the rest of customer_data
    #         customer_error = validate_payload_data(self, customer_data, CustomerSerializer)
    #     else:
    #         customer_error = ["customer_data is required."]

    #     # Validate customer_attachments
    #     attachments_data = given_data.pop('customer_attachments', None)
    #     if attachments_data:
    #         attachment_error = validate_multiple_data(self, attachments_data, CustomerAttachmentsSerializers, ['customer_id'])
    #     else:
    #         attachment_error = []

    #     # Validate customer_addresses
    #     addresses_data = given_data.pop('customer_addresses', None)
    #     if addresses_data:
    #         addresses_error = validate_multiple_data(self, addresses_data, CustomerAddressesSerializers, ['customer_id'])
    #     else:
    #         addresses_error = []
            
    #     # Validate custom_field_values
    #     custom_fields_data = given_data.get('custom_field_values', None)
    #     if custom_fields_data:
    #         custom_fields_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'])
    #     else:
    #         custom_fields_error = []

    #     # Check for mandatory fields
    #     if not customer_data or not addresses_data:
    #         logger.error("Customers, Customer Addresses data are mandatory but not provided.")
    #         return build_response(0, "Customers, Customer Addresses data are mandatory", [], status.HTTP_400_BAD_REQUEST)

    #     # Collect validation errors
    #     errors = {}
    #     if customer_error:
    #         errors["customer_data"] = customer_error
    #     if attachment_error:
    #         errors['customer_attachments'] = attachment_error
    #     if addresses_error:
    #         errors['customer_addresses'] = addresses_error
    #     if custom_fields_error:
    #         errors['custom_field_values'] = custom_fields_error
    #     if errors:
    #         return build_response(0, "ValidationError:", errors, status.HTTP_400_BAD_REQUEST)

    #     # Create Customer Data
    #     new_customer_data = generic_data_creation(self, [customer_data], CustomerSerializer)
    #     customer_id = new_customer_data[0].get("customer_id", None)
    #     logger.info('Customer - created*')

    #     # Create CustomerAttachment Data
    #     update_fields = {'customer_id': customer_id}
    #     if attachments_data:
    #         attachments_data = generic_data_creation(self, attachments_data, CustomerAttachmentsSerializers, update_fields)
    #         logger.info('CustomerAttachments - created*')
    #     else:
    #         attachments_data = []

    #     # Create CustomerAddress Data
    #     addresses_data = generic_data_creation(self, addresses_data, CustomerAddressesSerializers, update_fields)
    #     logger.info('CustomerAddresses - created*')

    #     # Handle CustomFieldValues
    #     custom_fields_data = given_data.pop('custom_field_values', None)
    #     if custom_fields_data:
    #         # Link each custom field value to the new customer
    #         for custom_field in custom_fields_data:
    #             custom_field['custom_id'] = customer_id  # Set the newly created customer ID
    #         custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer)
    #         logger.info('CustomFieldValues - created*')
    #     else:
    #         custom_fields_data = []

    #     # Build the response with all created data
    #     custom_data = [
    #         {"customer_data": new_customer_data[0]},
    #         {"customer_attachments": attachments_data},
    #         {"customer_addresses": addresses_data},
    #         {"custom_field_values": custom_fields_data}
    #     ]

    #     return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)
    
    def create(self, request, *args, **kwargs):
        given_data = request.data
        print("Given data:", given_data)
        # use_db = 'default'
        # Extract customer_data from the request
        customer_data = given_data.pop('customer_data', None)

        # Validate customer_data
        if customer_data:
            # Check if 'picture' exists in customer_data and is a list
            picture_data = customer_data.get('picture', None)
            if picture_data:
                if not isinstance(picture_data, list):
                    return build_response(0, "'picture' field in customer_data must be a list.", [], status.HTTP_400_BAD_REQUEST)

                for attachment in picture_data:
                    if not all(key in attachment for key in ['uid', 'name', 'attachment_name', 'file_size', 'attachment_path']):
                        return build_response(0, "Missing required fields in some picture data.", [], status.HTTP_400_BAD_REQUEST)

            # Validate the rest of customer_data
            customer_error = validate_payload_data(self, customer_data, CustomerSerializer)
        else:
            customer_error = ["customer_data is required."]

        # Validate customer_attachments
        attachments_data = given_data.pop('customer_attachments', None)
        if attachments_data:
            attachment_error = validate_multiple_data(self, attachments_data, CustomerAttachmentsSerializers, ['customer_id'], using_db=set_db('default'))
        else:
            attachment_error = []

        # Validate customer_addresses
        addresses_data = given_data.pop('customer_addresses', None)
        if addresses_data:
            addresses_error = validate_multiple_data(self, addresses_data, CustomerAddressesSerializers, ['customer_id'], using_db=set_db('default'))
        else:
            addresses_error = []

        # Validate custom_field_values
        custom_fields_data = given_data.get('custom_field_values', None)
        if custom_fields_data:
            custom_fields_error = validate_multiple_data(self, custom_fields_data, CustomFieldValueSerializer, ['custom_id'], using_db=set_db('default'))
        else:
            custom_fields_error = []

        # Check for mandatory fields
        if not customer_data or not addresses_data:
            logger.error("Customers, Customer Addresses data are mandatory but not provided.")
            return build_response(0, "Customers, Customer Addresses data are mandatory", [], status.HTTP_400_BAD_REQUEST)

        # Collect validation errors
        errors = {}
        if customer_error:
            errors["customer_data"] = customer_error
        if attachment_error:
            errors['customer_attachments'] = attachment_error
        if addresses_error:
            errors['customer_addresses'] = addresses_error
        if custom_fields_error:
            errors['custom_field_values'] = custom_fields_error
        if errors:
            return build_response(0, "ValidationError:", errors, status.HTTP_400_BAD_REQUEST)

        # Step 1: Create Customer Data in devcnl
        new_customer_data = generic_data_creation(self, [customer_data], CustomerSerializer, using=set_db('default'))
        customer_id = new_customer_data[0].get("customer_id", None)
        logger.info('Customer - created*')

        # # Step 2: Create entry in mstcnl.customers table
        # from your_app.models import Companies, CustomersMstModel  # Adjust this import based on your project structure

        customer_name = new_customer_data[0].get("name")
        phone = new_customer_data[0].get("phone")
        email = new_customer_data[0].get("email")
        company_id = new_customer_data[0].get("company_id")

        try:
            company = Companies.objects.first()
            print("-"*20)
            print("company : ", company)
            print("-"*20)
            company_id = company.company_id
            company_name = company.name
            phone = addresses_data[0].get("phone") if addresses_data else None
            print("phone : ", phone)
            email = addresses_data[0].get("email") if addresses_data else None
            print("email : ", email)
            # Create the record in mstcnl DB
            CustomersMstModel.objects.using('mstcnl').create(
                customer_id=customer_id,
                name=customer_name,
                phone=phone,
                email=email,
                company_id=company_id,
                company_name=company_name
            )
            logger.info("Customer also created in mstcnl.customers table")

        except Companies.DoesNotExist:
            logger.warning(f"Company with ID {company_id} not found. Skipping mstcnl customer creation.")

        # Step 3: Create CustomerAttachment Data
        update_fields = {'customer_id': customer_id}
        if attachments_data:
            attachments_data = generic_data_creation(self, attachments_data, CustomerAttachmentsSerializers, update_fields, using=set_db('default'))
            logger.info('CustomerAttachments - created*')
        else:
            attachments_data = []

        # Step 4: Create CustomerAddress Data
        addresses_data = generic_data_creation(self, addresses_data, CustomerAddressesSerializers, update_fields, using=set_db('default'))
        logger.info('CustomerAddresses - created*')

        # Step 5: Handle CustomFieldValues
        custom_fields_data = given_data.pop('custom_field_values', None)
        if custom_fields_data:
            for custom_field in custom_fields_data:
                custom_field['custom_id'] = customer_id
            custom_fields_data = generic_data_creation(self, custom_fields_data, CustomFieldValueSerializer, using=set_db('default'))
            logger.info('CustomFieldValues - created*')
        else:
            custom_fields_data = []

        # Step 6: Build response
        custom_data = [
            {"customer_data": new_customer_data[0]},
            {"customer_attachments": attachments_data},
            {"customer_addresses": addresses_data},
            {"custom_field_values": custom_fields_data}
        ]

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

            # Vlidated Customer Data
            customer_data = given_data.pop('customer_data', None)
            if customer_data:                
                customer_error = validate_payload_data(self, customer_data , CustomerSerializer)

            # Vlidated CustomerAttachment Data
            attachments_data = given_data.pop('customer_attachments', None)
            if attachments_data:
                exclude_fields = ['customer_id']
                attachments_error = validate_put_method_data(self, attachments_data,CustomerAttachmentsSerializers, exclude_fields, CustomerAttachments, current_model_pk_field='attachment_id')
            else:
                attachments_error = [] # Since 'CustomerAttachment' is optional, so making an error is empty list

            # Vlidated CustomerAddresses Data
            addresses_data = given_data.pop('customer_addresses', None)
            if addresses_data:
                exclude_fields = ['customer_id']
                addresses_error = validate_put_method_data(self, addresses_data,CustomerAddressesSerializers, exclude_fields, CustomerAddresses, current_model_pk_field='customer_addresses_id')
                
            # Validated CustomFieldValues Data
            custom_field_values_data = given_data.pop('custom_field_values', None)
            if custom_field_values_data:
                exclude_fields = ['entity_data_id']
                custom_field_values_error = validate_put_method_data(self, custom_field_values_data, CustomFieldValueSerializer, exclude_fields, CustomFieldValue, current_model_pk_field='custom_field_value_id')
            else:
                custom_field_values_error = []  # Optional, so initialize as an empty list

            # Ensure mandatory data is present
            if not customer_data or not addresses_data:
                logger.error("Customer data and Customer addresses data are mandatory but not provided.")
                return build_response(0, "Customer and Customer addresses are mandatory", [], status.HTTP_400_BAD_REQUEST)
            
            errors = {}
            if customer_error:
                errors["customer_data"] = customer_error
            if attachments_error:
                errors["customer_attachments"] = attachments_error
            if addresses_error:
                errors['customer_addresses'] = addresses_error
            if custom_field_values_error:
                errors['custom_field_values'] = custom_field_values_error
            if errors:
                return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
            
            # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
            if customer_data:
                update_fields = []# No need to update any fields
                customer_data = update_multi_instances(self, pk, [customer_data], Customer, CustomerSerializer, update_fields,main_model_related_field='customer_id', current_model_pk_field='customer_id')

            # Update CustomerAttachment Data
            update_fields = {'customer_id':pk}
            attachments_data = update_multi_instances(self,pk, attachments_data,CustomerAttachments,CustomerAttachmentsSerializers, update_fields, main_model_related_field='customer_id', current_model_pk_field='attachment_id')

            # Update CustomerAddress Data
            addresses_data = update_multi_instances(self,pk, addresses_data,CustomerAddresses, CustomerAddressesSerializers, update_fields, main_model_related_field='customer_id', current_model_pk_field='customer_address_id')
            
            # Update CustomFieldValues Data
            if custom_field_values_data:
                custom_field_values_data = update_multi_instances(self, pk, custom_field_values_data, CustomFieldValue, CustomFieldValueSerializer, {}, main_model_related_field='custom_id', current_model_pk_field='custom_field_value_id')

            # --------------------------- M S T C N L   S Y N C ----------------------------------- #
            try:
                mst_customer = CustomersMstModel.objects.using('mstcnl').filter(customer_id=pk).first()

                if mst_customer:
                    customer_name = customer_data[0].get('name')
                    company = Companies.objects.first()
                    phone = addresses_data[0].get("phone") if addresses_data else None
                    email = addresses_data[0].get("email") if addresses_data else None
                    
                    # Update fields explicitly
                    mst_customer.name = customer_name
                    mst_customer.phone = phone
                    mst_customer.email = email
                    mst_customer.company_id = company.company_id if company else None
                    mst_customer.company_name = company.name if company else None
                    mst_customer.save(using='mstcnl')

                    logger.info("Customer updated successfully in mstcnl database.")
                else:
                    logger.warning(f"No customer found in mstcnl with customer_id = {pk}")
            except Exception as e:
                logger.warning(f"Error updating mstcnl record: {str(e)}")
                
            custom_data = [
                {"customer_data":customer_data},
                {"customer_attachments":attachments_data if attachments_data else []},
                {"customer_addresses":addresses_data if addresses_data else []},
                {"custom_field_values": custom_field_values_data if custom_field_values_data else []}  # Add custom field values to response
            ]

            return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
        
    def get_customer_payment_report(self, request):
        """
        Fetches a report of all payments received from customers.
        Shows payment details with customer and invoice information.
        """
        logger.info("Retrieving customer payment report data")
        page, limit = self.get_pagination_params(request)
        
        try:
            # Import required finance models
            from apps.finance.models import PaymentTransaction
            from apps.customer.filters import CustomerPaymentReportFilter
            
            # Base query - filter payments related to sales (received from customers)
            queryset = PaymentTransaction.objects.filter(
                order_type='Sale',
                transaction_type='Credit'  # Credit transactions represent payments received from customers
            )
            
            # Order by payment date (most recent first)
            queryset = queryset.order_by('-payment_date')
            
            # Apply any additional filters from the request
            if request.query_params:
                filterset = CustomerPaymentReportFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
            
            # Get total count for pagination
            total_count = queryset.count()
            
            # Apply pagination
            if page and limit:
                start_idx = (page - 1) * limit
                end_idx = start_idx + limit
                queryset = queryset[start_idx:end_idx]
            
            # Serialize the filtered data
            serializer = CustomerPaymentReportSerializer(queryset, many=True)
            
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error generating customer payment report: {str(e)}")
            return build_response(0, "An error occurred while generating the report", [], status.HTTP_500_INTERNAL_SERVER_ERROR)



class CustomerBalanceView(APIView):
    def post(self, request, customer_id, remaining_payment): 
        '''update_customer_balance_after payment transaction. This is used in the apps.sales.view.PaymentTransactionAPIView class.'''  
        try:
            customer_instance = Customer.objects.get(customer_id=customer_id)
            customer_balance = CustomerBalance.objects.filter(customer_id=customer_instance)

            if customer_balance.exists():
                # Update balance if customer balance already exists
                for balance in customer_balance:
                    customer_balance.update(balance_amount= balance.balance_amount + remaining_payment)
            else:
                # Create a new CustomerBalance entry if it doesn't exist
                CustomerBalance.objects.create(customer_id=customer_instance, balance_amount=remaining_payment)
    
        except ObjectDoesNotExist as e:
            return build_response(1, f"Customer with ID {customer_id} does not exist.", str(e), status.HTTP_404_NOT_FOUND)

        return build_response(1, "Balance Updated In Customer Balance Table", [], status.HTTP_201_CREATED)
    
    def get(self, request, pk=None):
        if pk:
            try:
                customer_id = get_object_or_404(Customer, pk=pk)
                balance = get_object_or_404(CustomerBalance, customer_id=customer_id)
                serializer = CustomerBalanceSerializer(balance)
                return build_response(1, "Customer Balance", serializer.data, status.HTTP_200_OK)
            except Exception as e:
                return build_response(1, "Something Went Wrong", str(e), status.HTTP_403_FORBIDDEN)
        else:
            balances = CustomerBalance.objects.all()
            serializer = CustomerBalanceSerializer(balances, many=True)
            return build_response(len(serializer.data), "Customer Balance", serializer.data, status.HTTP_200_OK)

    def update():
        pass