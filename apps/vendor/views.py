import logging
from django.db import transaction
from django.forms import ValidationError
from django.shortcuts import render,get_object_or_404
from django.http import  Http404
from rest_framework import viewsets,status
from rest_framework.views import APIView
from rest_framework.serializers import ValidationError

from apps.customfields.models import CustomFieldValue
from apps.customfields.serializers import CustomFieldValueSerializer
from apps.vendor.filters import VendorAgentFilter, VendorCategoryFilter, VendorFilter, VendorPaymentTermsFilter
from config.utils_filter_methods import filter_response, list_filtered_objects
from .models import Vendor, VendorCategory, VendorPaymentTerms, VendorAgent, VendorAttachment, VendorAddress
from .serializers import VendorSerializer, VendorCategorySerializer, VendorPaymentTermsSerializer, VendorAgentSerializer, VendorAttachmentSerializer, VendorAddressSerializer, VendorsOptionsSerializer
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
    """
    API ViewSet for handling vendor creation and related data.
    """
    def get_object(self, pk):
        try:
            return Vendor.objects.get(pk=pk)
        except Vendor.DoesNotExist:
            logger.warning(f"Vendor with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
       
    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result =  validate_input_pk(self,kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs) 
        try:
            summary = request.query_params.get("summary", "false").lower() == "true&" 
            if summary:
                logger.info("Retrieving vendors summary")
                vendors = Vendor.objects.all().order_by('-created_at')
                data = VendorsOptionsSerializer.get_vendors_summary(vendors)
                return build_response(len(data), "Success", data, status.HTTP_200_OK)
 
            logger.info("Retrieving all vendors")
            queryset = Vendor.objects.all().order_by('-created_at')

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = Vendor.objects.count()
             
            # Apply filters manually
            if request.query_params:
                filterset = VendorFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs

            serializer = VendorsOptionsSerializer(queryset, many=True)
            logger.info("vendors data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
 
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
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
        if not vendors_data or not vendor_addresses_data or not custom_fields_data:
            logger.error("Vendor data, vendor addresses data, and Custom Fields data are mandatory but not provided.")
            return build_response(0, "Vendor, vendor addresses, and Custom Fields are mandatory", [], status.HTTP_400_BAD_REQUEST)
        
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
            custom_field_values_data = update_multi_instances(self, pk, custom_field_values_data, CustomFieldValue, CustomFieldValueSerializer, {}, main_model_related_field='vendor_id', current_model_pk_field='custom_field_value_id')

        custom_data = [
            {"vendor_data":Vendor_data},
            {"vendor_attachments":attachments_data if attachments_data else []},
            {"vendor_addresses":addresses_data if addresses_data else []},
            {"custom_field_values": custom_field_values_data if custom_field_values_data else []}  # Add custom field values to response
        ]

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)