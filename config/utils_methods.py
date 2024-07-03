#utils_methods file
import logging
# from django.forms import ValidationError
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.db import models
import uuid,django_filters
from django.db.models import Q
from uuid import uuid4
from uuid import UUID
import base64
import os
import json
from django.utils import timezone
from django.db import models
from django.core.cache import cache


# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

# -------------- File Path Handler (for Vendor model only)----------------------
def custom_upload_to(instance, filename):
    file_extension = filename.split('.')[-1]
    unique_id = uuid4().hex[:7]  # Generate a unique ID (e.g., using UUID)
    new_filename = f"{unique_id}_{filename}"
    new_filename = new_filename.replace(' ', '_')
    return os.path.join('vendor', str(instance.name), new_filename)
# ---------------------------------------------------------

#functions for demonstration purposes
def encrypt(text):
    if text is None:
        return None
    # Encode the text using base64
    encoded_bytes = base64.b64encode(text.encode("utf-8"))
    encrypted_text = encoded_bytes.decode("utf-8")
    return encrypted_text

def decrypt(encrypted_text):
    if encrypted_text is None:
        return None
    # Decode the text using base64
    decoded_bytes = base64.b64decode(encrypted_text.encode("utf-8"))
    decrypted_text = decoded_bytes.decode("utf-8")
    return decrypted_text

class EncryptedTextField(models.TextField):
    """
    A custom field to store encrypted text.
    """
    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        try:
            # Attempt to decrypt the value
            return decrypt(value)
        except Exception as e:
            # Handle decryption errors gracefully
            return None
        # Implement decryption logic here
        return decrypt(value)

    def to_python(self, value):
        if isinstance(value, str):
            # Implement decryption logic here
            return decrypt(value)
        return value
 
    def get_prep_value(self, value):
        # Implement encryption logic here
        return encrypt(value)


#If you want to decrypt then you can uncomment this and run... in output you will find the decrypted account number 
# # Encoded account number
encoded_account_number = ""

# Decode from base64
decoded_bytes = base64.b64decode(encoded_account_number)

# Convert bytes to string
original_account_number = decoded_bytes.decode("utf-8")

#=======================Filters for primary key===============================================
def filter_uuid(queryset, name, value):
    try:
        uuid.UUID(value)
    except ValueError:
        return queryset.none()
    return queryset.filter(Q(**{name: value}))
#======================================================================

def build_response(count, message, data, status_code, errors=None):
    """
    Builds a standardized API response.
    """
    response = {
        'count': count,
        'message': message,
        'data': data
    }
    if errors:
        response['errors'] = errors
    return Response(response, status=status_code)

def list_all_objects(self, request, *args, **kwargs):
    queryset = self.filter_queryset(self.get_queryset())
    serializer = self.get_serializer(queryset, many=True)
    message = "NO RECORDS INSERTED" if not serializer.data else None
    return build_response(queryset.count(), message, serializer.data, status.HTTP_201_CREATED if not serializer.data else status.HTTP_200_OK)

def create_instance(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        data = serializer.data
        return build_response(1, "Record created successfully", data, status.HTTP_201_CREATED)
    else:
        errors_str = json.dumps(serializer.errors, indent=2)
        logger.error("Serializer validation error: %s", errors_str)
        return build_response(0, "Form validation failed", [], status.HTTP_400_BAD_REQUEST)

def update_instance(self, request, *args, **kwargs):
    partial = kwargs.pop('partial', False)
    instance = self.get_object()
    serializer = self.get_serializer(instance, data=request.data, partial=partial)
    serializer.is_valid(raise_exception=True)
    self.perform_update(serializer)
    data = serializer.data
    return build_response(1, "Record updated successfully", data, status.HTTP_200_OK)

def perform_update(self, serializer):
    serializer.save()  # Add any custom logic for updating if needed

#==================================================
#Patterns

def generate_order_number(order_type_prefix):
    """
    Generate an order number based on the given prefix and the current date.

    Args:
        order_type_prefix (str): The prefix for the order type.

    Returns:
        str: The generated order number.
    """
    current_date = timezone.now()
    date_str = current_date.strftime('%y%m')

    key = f"{order_type_prefix}-{date_str}"
    sequence_number = cache.get(key, 0)
    sequence_number += 1
    cache.set(key, sequence_number, timeout=None)

    sequence_number_str = f"{sequence_number:05d}"
    order_number = f"{order_type_prefix}-{date_str}-{sequence_number_str}"
    return order_number

class OrderNumberMixin(models.Model):
    order_no_prefix = ''
    order_no_field = ''

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        """
        Override the save method to generate and set the order number if it is not already set.
        """
        if not getattr(self, self.order_no_field):
            setattr(self, self.order_no_field, generate_order_number(self.order_no_prefix))
        super().save(*args, **kwargs)
#======================================================================================================
#It removes fields from role_permissions for sending Proper data to frontend team after successfully login
def remove_fields(obj):
    if isinstance(obj, dict):
        obj.pop('created_at', None)
        obj.pop('updated_at', None)
        for value in obj.values():
            remove_fields(value)
    elif isinstance(obj, list):
        for item in obj:
            remove_fields(item)

#====================================== API- Bulk Data CURD Operation-Requirements ===============================================

def get_object_or_none(model, **kwargs):
    """
    Fetches a single object from the database or returns None if not found.
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

def delete_multi_instance(del_value, main_model_class, related_model_class, main_model_field_name=None):
    """
    Deletes instances from a related model based on a field value from the main model.

    :param del_value: Value of the main model field to filter related model instances.
    :param main_model_class: The main model class.
    :param related_model_class: The related model class from which to delete instances.
    :param main_model_field_name: The field name in the related model that references the main model.
    """
    try:
        # Get the main model's primary key field name
        main_model_pk_field_name = main_model_class._meta.pk.name

        # Arrange arguments to filter
        filter_kwargs = {main_model_field_name or main_model_pk_field_name: del_value}

        # Delete related instances
        deleted_count, _ = related_model_class.objects.filter(**filter_kwargs).delete()
        logger.info(f"Deleted {deleted_count} instances from {related_model_class.__name__} where {filter_kwargs}.")
    except Exception as e:
        logger.error(f"Error deleting instances from {related_model_class.__name__}: {str(e)}")
        return False
    return True

def validate_multiple_data(self, bulk_data, model_serializer, exclude_fields):
        errors = []
        
        # Validate child data
        child_serializers = []
        for data in bulk_data:
            child_serializer = model_serializer(data=data)
            if not child_serializer.is_valid(raise_exception=False):
                error = child_serializer.errors
                exclude_keys = exclude_fields
                # Create a new dictionary excluding specified keys
                filtered_data = {k: v for k, v in error.items() if k not in exclude_keys}
                if filtered_data:
                    errors.append(filtered_data)

        return errors

def validate_payload_data(self, data , model_serializer):
        errors = []

        # Validate parent data
        serializer = model_serializer(data=data)
        # If Main model data is not valid
        if not serializer.is_valid(raise_exception=False):
            error = serializer.errors
            model = serializer.Meta.model
            model_name = model.__name__
            logger.error("Validation error on %s: %s",model_name, str(error))  # Log validation error
            errors.append(error)
        
        return errors

def generic_data_creation(self, valid_data, serializer_class, update_fields=None):
    '''
    ** This function creates new instances with valid data & at the same time it updates the data with required fields**
    valid_data - The data to be created
    serializer_class - name of the serializer for which the data is to be created.
    update_fields - fields to be updated before the data is created [input type dict]
    '''
    # If any fields to be updated before the data is created
    if update_fields:
        for data in valid_data:
            for key, value in update_fields.items():
                data[key] = value

    data_list = []
    for data in valid_data:
        serializer = serializer_class(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        data_list.append(serializer.data)

    return data_list

# Validates the input 'pk'
def validate_input_pk(self, pk=None):
    try:
        UUID(pk, version=4)
    except ValueError:
        logger.info('Invalid UUID provided')
        return build_response(0, "Invalid UUID provided", [], status.HTTP_404_NOT_FOUND)

def update_multi_instances(self, pk, valid_data, related_model_name, related_class_name, update_fields, main_model_related_field=None, current_model_pk_field=None):
    '''
    related_model_class : name of the current model Name
    main_model_related_field : This field should have the relation with main Model
    '''
    data_list = []
    try:
        filter_kwargs = {main_model_related_field:pk}
        old_instances_list  = list(related_model_name.objects.filter(**filter_kwargs).values_list('pk', flat=True))
        old_instances_list = [str(uuid) for uuid in old_instances_list] # conversion 
    except Exception as e:
        logger.error(f"Error fetching instances from {related_model_name.__name__}: {str(e)}")

    # get the ids that are updated
    pks_in_update_data = []

    # prepare user provided pks and verify with the previous records
    update_count = 0
    for data in valid_data:
        id = data.get(current_model_pk_field,None) # get the primary key in updated data
        # update the data for avilable pks
        if id is not None:
            pks_in_update_data.append(id) # collecting how many ids are updated
            instance = related_model_name.objects.get(pk=id)
            # if given pk is avilable in old instances then update
            if id in old_instances_list:
                serializer = related_class_name(instance, data=data, partial=False)
                serializer.is_valid(raise_exception=True)
                serializer.save()
                data_list.append(serializer.data)
                update_count = update_count + 1
        # If there is no pk avilabe (id will be None), it is new record to create
        else:
            # create new record by using function 'generic_data_creation'
            new_instance = generic_data_creation(self,[data],related_class_name,update_fields=update_fields)
            if new_instance:
                data_list.append(new_instance[0]) # append the new record to existing records
            else:
                logger.warning("Error during update: new record creation failed in {related_model_name.__name__}")
                return build_response(0,f"Error during update: new record creation failed in {related_model_name.__name__}",[],status.HTTP_400_BAD_REQUEST)
            
    # Delete the previous records if those are not mentioned in update data
    for id in old_instances_list:
        if id not in pks_in_update_data:
            try:
                instance = related_model_name.objects.get(pk=id)
                instance.delete()
                logger.info(f'Old record in {related_model_name.__name__} with id {id} is deleted')
            except Exception as e:
                logger.warning(f'Error deleting the record in {related_model_name.__name__} with id {id}')
  
    if update_count == len(old_instances_list):
        logger.info(f'All old instances in {related_model_name.__name__} are updated')
        logger.info(f'Old instances count ={len(old_instances_list)}')

    return data_list

def validate_put_method_data(self, valid_data, serializer_name, update_fields, model_class_name, current_model_pk_field=None):

    error_list = []

    for data in valid_data:
        id = data.get(current_model_pk_field,None) # get the primary key in updated data
        # update the data for avilable pks
        if id is not None:
            instance = model_class_name.objects.filter(pk=id).first()
            serializer = serializer_name(instance,data=data)
            # If Main model data is not valid
            if not serializer.is_valid(raise_exception=False):
                error = serializer.errors
                model = serializer.Meta.model
                model_name = model.__name__
                logger.error("Validation error on %s: %s",model_name, str(error))  # Log validation error
                error_list.append(error)

        # If there is no pk avilabe (id will be None), validate the new record
        else:
            serializer = serializer_name(data=data)
            if not serializer.is_valid(raise_exception=False):
                error = serializer.errors
                exclude_keys = update_fields
                # Create a new dictionary excluding specified keys
                filtered_data = {k: v for k, v in error.items() if k not in exclude_keys}
                if filtered_data:
                    error_list.append(filtered_data)

    return error_list

def validate_order_type(data, error_list, model_name,look_up=None):
    '''
    data - the data to be validated
    error_list - the list contains erros
    model_name - Name of the model
    look_up - field that needs to be validated
    '''
    order_type = data.get(look_up,None) # 'order_type' is additonal Field and not defined in model
    if order_type is None:
        error_list.append({look_up:["This field may not be null."]})
    else:
        order_type = get_object_or_none(model_name, name=order_type)
        if order_type is None:
            if len(error_list) > 0:
                error_list[0][look_up] = ["Invalid order type."]
            else:
                error_list.append({look_up:["Invalid order type."]})

                
