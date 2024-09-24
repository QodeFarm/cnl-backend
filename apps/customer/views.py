from uuid import UUID
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from requests import request
from rest_framework import viewsets, generics, mixins as mi
from apps import customer
from apps.customer.filters import LedgerAccountsFilters, CustomerFilters, CustomerAddressesFilters, CustomerAttachmentsFilters
from config.utils_filter_methods import filter_response
from .models import *
from .serializers import *
from config.utils_methods import *
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
import logging
from django.db import transaction
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__) 

# Create your views here.

class LedgerAccountsViews(viewsets.ModelViewSet):
    queryset = LedgerAccounts.objects.all()
    serializer_class = LedgerAccountsSerializers
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = LedgerAccountsFilters
    ordering_fields = ['name', 'created_at', 'updated_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class CustomerViews(viewsets.ModelViewSet):
    queryset = Customer.objects.all()
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
        if "pk" in kwargs:
            result =  validate_input_pk(self,kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)

        try:
            summary = request.query_params.get("summary", "false").lower() == "true" + "&"
            if summary:
                logger.info("Retrieving customer summary")
                customers = Customer.objects.all()
                data = CustomerOptionSerializer.get_customer_summary(customers)
                return Response(data, status=status.HTTP_200_OK)
 
            logger.info("Retrieving all customers")
            queryset = Customer.objects.all()

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = Customer.objects.count()
             
            # Apply filters manually
            if request.query_params:
                filterset = CustomerFilters(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs

            serializer = CustomerOptionSerializer(queryset, many=True)
            logger.info("Customer data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

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

            # Customizing the response data
            custom_data = {
                "customer_data": customer_serializer.data,
                "customer_attachments": attachments_data,
                "customer_addresses": addresses_data
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
      
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a sale order and its related attachments and shipments.
        """
        try:
            # Get the Customer instance
            instance = Customer.objects.get(pk=pk)

            # Delete related CustomerAttachments and CustomerAddresses
            if not delete_multi_instance(pk, Customer, CustomerAttachments, main_model_field_name='customer_id'):
                return build_response(0, "Error deleting related order attachments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
            if not delete_multi_instance(pk, Customer, CustomerAddresses, main_model_field_name='customer_id'):
                return build_response(0, "Error deleting related order shipments", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main Customer instance
            instance.delete()

            logger.info(f"Customer with ID {pk} deleted successfully.")
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
    
    def create(self, request, *args, **kwargs):
        given_data = request.data
        print("Given data:", given_data)

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
            attachment_error = validate_multiple_data(self, attachments_data, CustomerAttachmentsSerializers, ['customer_id'])
        else:
            attachment_error = []

        # Validate customer_addresses
        addresses_data = given_data.pop('customer_addresses', None)
        if addresses_data:
            addresses_error = validate_multiple_data(self, addresses_data, CustomerAddressesSerializers, ['customer_id'])
        else:
            addresses_error = []

        if not customer_data or not addresses_data:
            logger.error("Customers and Customer Addresses are mandatory but not provided.")
            return build_response(0, "Customers and Customer Addresses are mandatory", [], status.HTTP_400_BAD_REQUEST)

        errors = {}
        if customer_error:
            errors["customer_data"] = customer_error
        if attachment_error:
            errors['customer_attachments'] = attachment_error
        if addresses_error:
            errors['customer_addresses'] = addresses_error
        if errors:
            return build_response(0, "ValidationError:", errors, status.HTTP_400_BAD_REQUEST)

        # Create Customer Data
        new_customer_data = generic_data_creation(self, [customer_data], CustomerSerializer)
        customer_id = new_customer_data[0].get("customer_id", None)
        logger.info('Customer - created*')

        # Create CustomerAttachment Data
        update_fields = {'customer_id': customer_id}
        if attachments_data:
            attachments_data = generic_data_creation(self, attachments_data, CustomerAttachmentsSerializers, update_fields)
            logger.info('CustomerAttachments - created*')
        else:
            attachments_data = []

        # Create CustomerAddress Data
        update_fields = {'customer_id': customer_id}
        addresses_data = generic_data_creation(self, addresses_data, CustomerAddressesSerializers, update_fields)
        logger.info('CustomerAddress - created*')

        # Build the response with customer_data including picture
        custom_data = [
            {"customer_data": new_customer_data[0]},
            {"customer_attachments": attachments_data},
            {"customer_addresses": addresses_data}
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

            custom_data = [
                {"customer_data":customer_data},
                {"customer_attachments":attachments_data if attachments_data else []},
                {"customer_addresses":addresses_data if addresses_data else []}
            ]

            return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
    

