from uuid import UUID
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from rest_framework import viewsets, generics, mixins as mi
from apps import customer
from apps.customer.filters import LedgerAccountsFilters, CustomerFilters, CustomerAddressesFilters, CustomerAttachmentsFilters
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
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request,  *args, **kwargs):
        if 'pk' in kwargs:
            result =  validate_input_pk(self,kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            instance = Customer.objects.all()
        except Customer.DoesNotExist:
            logger.error("Customer does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        else:
            serializer = CustomerSerializer(instance, many=True)
            logger.info("Customer data retrieved successfully.")
            return build_response(instance.count(), "Success", serializer.data, status.HTTP_200_OK)

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
        # Extracting data from the request
        given_data = request.data

        #---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """

        # Vlidated SaleOrder Data
        customer_data = given_data.pop('customer_data', None) # parent_data
        if customer_data:
            customer_error = validate_payload_data(self, customer_data, CustomerSerializer)

        # Vlidated CustomerAttachments Data
        attachments_data = given_data.pop('customer_attachments', None)
        if attachments_data:
            attachment_error = validate_multiple_data(self, attachments_data, CustomerAttachmentsSerializers,['customer_id'])
        else:
            attachment_error = [] # Since 'attachments_data' is optional, so making an error is empty list

        # Vlidated SaleOrderItems Data
        addresses_data = given_data.pop('customer_addresses', None)
        if addresses_data:
            addresses_error = validate_multiple_data(self, addresses_data, CustomerAddressesSerializers,['customer_id'])
        else:
            addresses_error = [] # Since 'addresses_data' is optional, so making an error is empty list

        # Ensure mandatory data is present
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
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
        
        #---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """
            
        # Hence the data is validated , further it can be created.

        # Create Customer Data
        new_customer_data = generic_data_creation(self, [customer_data], CustomerSerializer)
        customer_id = new_customer_data[0].get("customer_id",None) #Fetch customer_id from mew instance
        logger.info('Customer - created*')     

        # Create VendorAttachment Data
        update_fields = {'customer_id':customer_id}
        if attachments_data:
            attachments_data = generic_data_creation(self, attachments_data, CustomerAttachmentsSerializers, update_fields)
            logger.info('CustomerAttachments - created*')
        else:
            # Since CustomerAttachments Data is optional, so making it as an empty data list
            attachments_data = []

        # Create VendorAddress Data
        update_fields = {'customer_id':customer_id}
        addresses_data = generic_data_creation(self, addresses_data, CustomerAddressesSerializers, update_fields)
        logger.info('CustomerAddress - created*')

        custom_data = [
            {"customer_data":new_customer_data[0]},
            {"customer_attachments":attachments_data},
            {"customer_addresses":addresses_data}
        ]

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)        
 
#=============================================================================================================       
    
    def put(self, request, pk, *args, **kwargs):
        customer_data = attachments_data = addresses_data =  response_data = None
        errors = []
 
        partial = kwargs.pop('partial', False)
        instance = self.get_object(pk)
        serializer = CustomerSerializer(instance, data=request.data['customer_data'], partial=partial)
        try:
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        except Exception as e:
            logger.error("Validation error: %s", str(e))  # Log validation errors
            errors.append(str(e))  # Collect validation errors
        else:
            customer_data = serializer.data
 
            # Update customer_attachments
            customer_attachments_data = request.data.pop('customer_attachments')
            attachments_data, attachments_error = update_multi_instance(pk, customer_attachments_data, CustomerAttachments, CustomerAttachmentsSerializers, filter_field_1='customer_id')
            errors.extend(attachments_error)
            
            # Update customer_addresses
            customer_addresses_data = request.data.pop('customer_addresses')
            addresses_data, addresses_error = update_multi_instance(pk, customer_addresses_data, CustomerAddresses, CustomerAddressesSerializers, filter_field_1='customer_id')
            errors.extend(addresses_error)
            
            if errors:
                logger.warning("Record created with some errors: %s", errors)
                return build_response(1, "Record created with errors", response_data, status.HTTP_201_CREATED, errors)
            
        if customer_data or attachments_data or addresses_data :  
            custom_data = {
                "customer_data": customer_data,
                "customer_attachments": attachments_data,
                "customer_addresses":addresses_data
            }
            response_data = build_response(1, "Record updated successfully", custom_data, status.HTTP_200_OK)
        else:
            logger.error("Error in customerViewSet")
            response_data = build_response(0, "Record updation failed", [serializer.errors], status.HTTP_400_BAD_REQUEST)
       
        return response_data
 