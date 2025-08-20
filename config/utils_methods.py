# Grouped imports:
from rest_framework.permissions import BasePermission
from uuid import UUID, uuid4
import logging
import base64
import random
import string
import json
import uuid
import os

# Alphabetized imports:
import inflect
import requests
from django.conf import settings
from django.core.cache import cache
from django.core.mail import EmailMessage
from django.db import models, transaction
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

# from apps.sales.models import MstcnlSaleOrder, SaleOrder
from config.settings import MEDIA_ROOT, MEDIA_URL
import os
import logging
import openpyxl
from openpyxl.styles import PatternFill, Font, Alignment
from openpyxl.utils import get_column_letter
from openpyxl.comments import Comment
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
logger = logging.getLogger(__name__)




# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__) # Create a logger object

def custom_upload_to(instance, filename):
    ''' File Path Handler (for Vendor model only) '''
    file_extension = filename.split('.')[-1]
    unique_id = uuid4().hex[:7]  # Generate a unique ID (e.g., using UUID)
    new_filename = f"{unique_id}_{filename}"
    new_filename = new_filename.replace(' ', '_')
    return os.path.join('vendor', str(instance.name), new_filename)

def encrypt(text):
    ''' Functions for demonstration purposes '''
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

" NOTE : If you want to decrypt then you can uncomment this and run... in output you will find the decrypted account number "
encoded_account_number = "" # Encoded account number
decoded_bytes = base64.b64decode(encoded_account_number) # Decode from base64
original_account_number = decoded_bytes.decode("utf-8") # Convert bytes to string

#======================= POST / PUT / GET / BUILD RESPONSE =====================================================

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

def list_all_objects_1(self, request, *args, **kwargs):
    queryset = self.filter_queryset(self.get_queryset())
    serializer = self.get_serializer(queryset, many=True)
    message = "NO RECORDS INSERTED" if not serializer.data else None
    return build_response(queryset.count(), message, serializer.data, status.HTTP_201_CREATED if not serializer.data else status.HTTP_200_OK)

from itertools import chain

def list_all_objects(self, request, *args, **kwargs):
    try:
        filters = request.query_params.dict()
        sale_order_id = filters.get('sale_order_id')
        records_all = request.query_params.get("records_all", "false").lower() == "true"

        # Default queryset (from default DB)
        queryset = self.filter_queryset(self.get_queryset().order_by('-created_at'))

        #  Special logic: only if sale_order_id is provided
        if sale_order_id:
            default_qs = self.get_queryset().using('default').filter(sale_order_id=sale_order_id)
            mstcnl_qs = self.get_queryset().using('mstcnl').filter(sale_order_id=sale_order_id)

            if default_qs.exists():
                queryset = self.filter_queryset(default_qs.order_by('-created_at'))
            elif mstcnl_qs.exists():
                queryset = self.filter_queryset(mstcnl_qs.order_by('-created_at'))
            else:
                queryset = []  # not found in either DB

        #  records_all logic (combine both DBs)
        elif records_all:
            default_qs = self.filter_queryset(self.get_queryset().using('default').order_by('-created_at'))
            mstcnl_qs = self.filter_queryset(self.get_queryset().using('mstcnl').order_by('-created_at'))
            queryset = list(chain(default_qs, mstcnl_qs))

        #  All other cases = default logic is already active

        serializer = self.get_serializer(queryset, many=True)
        message = "NO RECORDS INSERTED" if not serializer.data else None

        return build_response(
            len(queryset),
            message,
            serializer.data,
            status.HTTP_201_CREATED if not serializer.data else status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"Error in list_all_objects: {str(e)}")
        return build_response(0, "Error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


def create_instance(self, request, *args, **kwargs):
    serializer = self.get_serializer(data=request.data)
    
    if serializer.is_valid():
        serializer.save()
        data = serializer.data
        return build_response(1, "Record created successfully", data, status.HTTP_201_CREATED)
    else:
        errors_str = json.dumps(serializer.errors, indent=2)
        logger.error("Serializer validation error: %s", errors_str)
        return build_response(0, "Form validation failed", [], errors = serializer.errors, status_code=status.HTTP_400_BAD_REQUEST)

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
    
    
def soft_delete(instance):
    instance.is_deleted = True
    instance.save()
    return Response(status=status.HTTP_204_NO_CONTENT)

#=========================== Patterns /  Order number related =====================================================

# def generate_order_number(order_type_prefix):
#     """
#     Generate an order number based on the given prefix and the current date.

#     Args:
#         order_type_prefix (str): The prefix for the order type.

#     Returns:
#         str: The generated order number.
#     """
#     if order_type_prefix == "PRD":
#         key = f"{order_type_prefix}"
#         sequence_number = cache.get(key, 0)
#         sequence_number += 1
#         cache.set(key, sequence_number, timeout=None)

#         sequence_number_str = f"{sequence_number:05d}"
#         order_number = f"{order_type_prefix}-{sequence_number_str}"
#     else:

#         current_date = timezone.now()
#         date_str = current_date.strftime('%y%m')

#         key = f"{order_type_prefix}-{date_str}"
#         sequence_number = cache.get(key, 0)
#         sequence_number += 1
#         cache.set(key, sequence_number, timeout=None)

#         sequence_number_str = f"{sequence_number:05d}"
#         order_number = f"{order_type_prefix}-{date_str}-{sequence_number_str}"
#     return order_number

#---------------------------pavan-end--------------------------------------------------

def generate_order_number(order_type_prefix, model_class=None, field_name=None, override_prefix=None):
    """
    Generate an order number using the last record in the database, safe against server restarts.

    Args:
        order_type_prefix (str): The prefix for the order type.
        model_class (Model): The model class to query for last number.
        field_name (str): The field name storing the order number (e.g., 'return_no').

    Returns:
        str: The generated order number.
    """
    current_date = timezone.now()
    date_str = current_date.strftime('%y%m')
    
    prefix = override_prefix if override_prefix else order_type_prefix

    if prefix == "PRD":
        if model_class and field_name:
            filter_kwargs = {f"{field_name}__startswith": prefix}
            last_record = model_class.objects.filter(**filter_kwargs).order_by(f"-{field_name}").first()
            last_number = 0
            if last_record:
                try:
                    last_number = int(getattr(last_record, field_name).split('-')[-1])
                except Exception:
                    last_number = 0
            return f"{prefix}-{last_number + 1:05d}"
        return f"{prefix}-00001"

    if prefix == "SOO":
        from apps.sales.models import SaleOrder, MstcnlSaleOrder
        filter_kwargs = {f"{field_name}__startswith": f"{prefix}-{date_str}"}
        
        last_default = SaleOrder.objects.using('default').filter(**filter_kwargs).order_by(f"-{field_name}").first()
        last_mstcnl = MstcnlSaleOrder.objects.using('mstcnl').filter(**filter_kwargs).order_by(f"-{field_name}").first()

        def extract_seq(obj):
            if not obj:
                return 0
            try:
                return int(getattr(obj, field_name).split('-')[-1])
            except Exception:
                return 0

        max_default = extract_seq(last_default)
        max_mstcnl = extract_seq(last_mstcnl)
        next_seq = max(max_default, max_mstcnl) + 1

        return f"{prefix}-{date_str}-{next_seq:05d}"
    
    if prefix == "SOO-INV":
        # ✅ Late import to avoid circular
        from apps.sales.models import SaleInvoiceOrders, MstcnlSaleInvoiceOrder
        filter_kwargs = {f"{field_name}__startswith": f"{prefix}-{date_str}"}

        last_default = SaleInvoiceOrders.objects.using('default').filter(**filter_kwargs).order_by(f"-{field_name}").first()
        last_mstcnl = MstcnlSaleInvoiceOrder.objects.using('mstcnl').filter(**filter_kwargs).order_by(f"-{field_name}").first()

        def extract_seq(obj):
            if not obj:
                return 0
            try:
                return int(getattr(obj, field_name).split('-')[-1])
            except Exception:
                return 0

        max_default = extract_seq(last_default)
        max_mstcnl = extract_seq(last_mstcnl)
        next_seq = max(max_default, max_mstcnl) + 1

        return f"{prefix}-{date_str}-{next_seq:05d}"
    
    if prefix == "PTR":
        from apps.sales.models import PaymentTransactions, MstCnlPaymentTransactions
        filter_kwargs = {f"{field_name}__startswith": f"{prefix}-{date_str}"}

        last_default = PaymentTransactions.objects.using('default').filter(**filter_kwargs).order_by(f"-{field_name}").first()
        last_mstcnl = MstCnlPaymentTransactions.objects.using('mstcnl').filter(**filter_kwargs).order_by(f"-{field_name}").first()

        def extract_seq(obj):
            if not obj:
                return 0
            try:
                return int(getattr(obj, field_name).split('-')[-1])
            except Exception:
                return 0

        max_default = extract_seq(last_default)
        max_mstcnl = extract_seq(last_mstcnl)
        next_seq = max(max_default, max_mstcnl) + 1

        return f"{prefix}-{date_str}-{next_seq:05d}"

    # Normal date-based flow — unchanged
    prefix = f"{order_type_prefix}-{date_str}"
    last_number = 0

    if model_class and field_name:
        filter_kwargs = {f"{field_name}__startswith": prefix}
        last_record = model_class.objects.filter(**filter_kwargs).order_by(f"-{field_name}").first()

        if last_record:
            try:
                last_number = int(getattr(last_record, field_name).split('-')[-1])
            except Exception:
                last_number = 0

    return f"{prefix}-{last_number + 1:05d}"

#----------------------------Pramod-end------------------------------------------------

class OrderNumberMixin(models.Model):
    order_no_prefix = ''
    order_no_field = ''

    class Meta:
        abstract = True
        
    def get_order_prefix(self):
        """
        Override to handle 'Other' sale type case
        and validate the prefix inline.
        """
        if hasattr(self, 'sale_type_id') and self.sale_type_id:
            if self.sale_type_id.name and self.sale_type_id.name.lower() == 'Other':
                return 'SOO'
        if hasattr(self, 'bill_type') and self.bill_type:
            if self.bill_type.lower() == 'Others':
                return 'SOO-INV'
        
        # Validate existing prefix before returning
        valid_prefixes = ['SO', 'SOO', 'PO', 'SO-INV', 'SR', 'PO-INV', 'PR', 'PRD', 'PTR']  # add all that you use
        if self.order_no_prefix not in valid_prefixes:
            raise ValueError("Invalid prefix")  # <== this will surface clearly

        return self.order_no_prefix
        
    # def get_order_prefix(self):
    #     """Method to be overridden by child classes for custom prefix logic"""
    #     return self.order_no_prefix

    def save(self, *args, **kwargs):
        """
        Override the save method to generate and set the order number if it is not already set.
        """
        if not getattr(self, self.order_no_field):
            prefix = self.get_order_prefix()
            setattr(self, self.order_no_field, generate_order_number(prefix))
        super().save(*args, **kwargs)

def increment_order_number(order_type_prefix):
    """
    Generate and increment an order number based on the given prefix and the current date.

    Args:
        order_type_prefix (str): The prefix for the order type.

    Returns:
        str: The generated order number.
    """
    # Handle prefixes without date-based sequences (e.g., PRD)
    if order_type_prefix == "PRD":
        key = f"{order_type_prefix}"
        sequence_number = cache.get(key, 0)
        sequence_number += 1
        cache.set(key, sequence_number, timeout=None)

        sequence_number_str = f"{sequence_number:05d}"
        return f"{order_type_prefix}-{sequence_number_str}"

    # Handle date-based sequences (e.g., SO-INV, SO, SHIP, etc.)
    current_date = timezone.now()
    date_str = current_date.strftime('%y%m')

    key = f"{order_type_prefix}-{date_str}"
    sequence_number = cache.get(key, 0) + 1
    cache.set(key, sequence_number, timeout=None)

    sequence_number_str = f"{sequence_number:05d}"
    return f"{order_type_prefix}-{date_str}-{sequence_number_str}"


#=========================== BULK DATA VALIDATIONS / CURD OPERATION-REQUIREMENTS ===================================
def normalize_value(value):
    '''Check if the value is a list containing exactly one empty dictionary or [empty_dict, None]'''
    if value == [{}] or value is None or value == [{}, None]:
        return []
    return value

def get_object_or_none(model, **kwargs):
    """
    Fetches a single object from the database or returns None if not found.
    """
    try:
        return model.objects.get(**kwargs)
    except model.DoesNotExist:
        return None

# def delete_multi_instance(del_value, main_model_class, related_model_class, main_model_field_name=None):
#     """
#     Deletes instances from a related model based on a field value from the main model.

#     :param del_value: Value of the main model field to filter related model instances.
#     :param main_model_class: The main model class.
#     :param related_model_class: The related model class from which to delete instances.
#     :param main_model_field_name: The field name in the related model that references the main model.
#     """
#     try:
#         # Get the main model's primary key field name
#         main_model_pk_field_name = main_model_class._meta.pk.name

#         # Arrange arguments to filter
#         filter_kwargs = {main_model_field_name or main_model_pk_field_name: del_value}

#         # Delete related instances
#         deleted_count, _ = related_model_class.objects.filter(**filter_kwargs).delete()
#         logger.info(f"Deleted {deleted_count} instances from {related_model_class.__name__} where {filter_kwargs}.")
#     except Exception as e:
#         logger.error(f"Error deleting instances from {related_model_class.__name__}: {str(e)}")
#         return False
#     return True

# def delete_multi_instance(del_value, main_model_class, related_model_class, main_model_field_name=None, using_db=None):
#     """
#     Deletes instances from a related model based on a field value from the main model.
#     Allows for database selection (using_db).

#     :param del_value: Value of the main model field to filter related model instances.
#     :param main_model_class: The main model class.
#     :param related_model_class: The related model class from which to delete instances.
#     :param main_model_field_name: The field name in the related model that references the main model.
#     :param using_db: The database to use for the deletion operation (e.g., 'mstcnl', 'devcnl').
#     """
#     try:
#         # Get the main model's primary key field name
#         main_model_pk_field_name = main_model_class._meta.pk.name

#         # Arrange arguments to filter
#         filter_kwargs = {main_model_field_name or main_model_pk_field_name: del_value}

#         # Delete related instances from the specified database
#         deleted_count, _ = related_model_class.objects.using(using_db).filter(**filter_kwargs).delete()
#         logger.info(f"Deleted {deleted_count} instances from {related_model_class.__name__} where {filter_kwargs}.")

#     except Exception as e:
#         logger.error(f"Error deleting instances from {related_model_class.__name__}: {str(e)}")
#         return False

#     return True

def delete_multi_instance(del_value, main_model_class, related_model_class, main_model_field_name=None, using_db=None):
    """
    Soft deletes instances from a related model by setting is_deleted=True,
    based on a field value from the main model. Allows for database selection (using_db).

    :param del_value: Value of the main model field to filter related model instances.
    :param main_model_class: The main model class.
    :param related_model_class: The related model class from which to soft delete instances.
    :param main_model_field_name: The field name in the related model that references the main model.
    :param using_db: The database to use for the operation (e.g., 'mstcnl', 'devcnl').
    """
    try:
        main_model_pk_field_name = main_model_class._meta.pk.name
        filter_kwargs = {main_model_field_name or main_model_pk_field_name: del_value}

        related_qs = related_model_class.objects.using(using_db) if using_db else related_model_class.objects
        related_instances = related_qs.filter(**filter_kwargs)

        count = 0
        for instance in related_instances:
            instance.is_deleted = True
            if using_db:
                instance.save(using=using_db)
            else:
                instance.save()
            count += 1

        logger.info(f"Soft deleted {count} instances from {related_model_class.__name__} where {filter_kwargs}.")

    except Exception as e:
        logger.error(f"Error soft deleting instances from {related_model_class.__name__}: {str(e)}")
        return False

    return True



# def validate_multiple_data(self, bulk_data, model_serializer, exclude_fields):
#         errors = []

#         if bulk_data:
#             if isinstance(bulk_data, list):
#                 bulk_data = bulk_data
#             if isinstance(bulk_data, dict):
#                 bulk_data = [bulk_data]
        
#         # Validate child data
#         child_serializers = []
#         for data in bulk_data:
#             child_serializer = model_serializer(data=data)
#             if not child_serializer.is_valid(raise_exception=False):
#                 error = child_serializer.errors
#                 exclude_keys = exclude_fields
#                 # Create a new dictionary excluding specified keys
#                 filtered_data = {k: v for k, v in error.items() if k not in exclude_keys}
#                 if filtered_data:
#                     errors.append(filtered_data)

#         return errors

def validate_multiple_data(self, bulk_data, model_serializer, exclude_fields, using_db=None):
    errors = []

    if bulk_data:
        if isinstance(bulk_data, list):
            bulk_data = bulk_data
        if isinstance(bulk_data, dict):
            bulk_data = [bulk_data]

    # Validate child data
    child_serializers = []
    for data in bulk_data:
        # Pass using_db to the model_serializer to handle database context properly
        child_serializer = model_serializer(data=data, context={'using_db': using_db})
        if not child_serializer.is_valid(raise_exception=False):
            error = child_serializer.errors
            exclude_keys = exclude_fields
            # Create a new dictionary excluding specified keys
            filtered_data = {k: v for k, v in error.items() if k not in exclude_keys}
            if filtered_data:
                errors.append(filtered_data)

    return errors



def validate_payload_data(self, data , model_serializer, using='default'):
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

# def generic_data_creation(self, valid_data, serializer_class, update_fields=None, using='default'):
#     '''
#     ** This function creates new instances with valid data & at the same time it updates the data with required fields**
#     valid_data - The data to be created
#     serializer_class - name of the serializer for which the data is to be created.
#     update_fields - fields to be updated before the data is created [input type dict]
#     '''
#     # If any fields to be updated before the data is created
#     if update_fields:
#         for data in valid_data:
#             for key, value in update_fields.items():
#                 data[key] = value

#     data_list = []
#     for data in valid_data:
#         serializer = serializer_class(data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         data_list.append(serializer.data)

#     return data_list

def generic_data_creation(self, valid_data, serializer_class, update_fields=None, using='default'):
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

        #  This is the only line added to respect the 'using' parameter
        instance = serializer.Meta.model.objects.db_manager(using).create(**serializer.validated_data)
        serializer = serializer_class(instance)

        data_list.append(serializer.data)

    return data_list


# def generic_data_creation(self, valid_data, serializer_class, update_fields=None, using=None):
#     '''
#     Generic function to create instances - remains completely table-agnostic
#     '''
#     if isinstance(valid_data, dict):
#         valid_data = [valid_data]
#         return_as_dict = True
#     else:
#         return_as_dict = False

#     if update_fields:
#         for data in valid_data:
#             data.update(update_fields)

#     data_list = []
#     for data in valid_data:
#         serializer = serializer_class(data=data)
#         serializer.is_valid(raise_exception=True)
        
#         if using:
#             ModelClass = serializer.Meta.model
#             instance = ModelClass.objects.using(using).create(**serializer.validated_data)
#             serializer = serializer_class(instance)
#         else:
#             instance = serializer.save()
            
#         data_list.append(serializer.data)

#     return data_list[0] if return_as_dict else data_list

def validate_input_pk(self, pk=None):
    try:
        UUID(pk, version=4)
    except ValueError:
        logger.info('Invalid UUID provided')
        return build_response(0, "Invalid UUID provided", [], status.HTTP_404_NOT_FOUND)

def filter_uuid(queryset, name, value):
    try:
        uuid.UUID(value)
    except ValueError:
        return queryset.none()
    return queryset.filter(Q(**{name: value}))

def update_multi_instances(self, pk, valid_data, related_model_name, related_class_name, update_fields, main_model_related_field=None, current_model_pk_field=None, using_db='default'):
    '''
    related_model_name : name of the current model class
    main_model_related_field : This field should have the relation with main Model
    '''
    data_list = []
    try:
        filter_kwargs = {main_model_related_field: pk}
        old_instances_list = list(
            related_model_name.objects.using(using_db).filter(**filter_kwargs).values_list('pk', flat=True)
        )
        old_instances_list = [str(uuid) for uuid in old_instances_list]  # conversion 
    except Exception as e:
        logger.error(f"Error fetching instances from {related_model_name.__name__}: {str(e)}")

    pks_in_update_data = []

    if valid_data:
        if isinstance(valid_data, list):
            valid_data = valid_data
        if isinstance(valid_data, dict):
            valid_data = [valid_data]

    update_count = 0
    for data in valid_data:
        id = data.get(current_model_pk_field, None)  # get the primary key in updated data
        if id is not None:
            pks_in_update_data.append(id)
            instance = related_model_name.objects.using(using_db).get(pk=id)
            if id in old_instances_list:
                serializer = related_class_name(instance, data=data, partial=False)
                serializer.is_valid(raise_exception=True)
                serializer.save(using=using_db)
                data_list.append(serializer.data)
                update_count += 1
        else:
            new_instance = generic_data_creation(self, [data], related_class_name, update_fields=update_fields)
            if new_instance:
                data_list.append(new_instance[0])
                logger.info(f'New instance in {related_model_name.__name__} is created')
            else:
                logger.warning(f"Error during update: new record creation failed in {related_model_name.__name__}")
                return build_response(0, f"Error during update: new record creation failed in {related_model_name.__name__}", [], status.HTTP_400_BAD_REQUEST)

    for id in old_instances_list:
        if id not in pks_in_update_data:
            try:
                instance = related_model_name.objects.using(using_db).get(pk=id)
                instance.delete()
                logger.info(f'Old record in {related_model_name.__name__} with id {id} is deleted')
            except Exception as e:
                logger.warning(f'Error deleting the record in {related_model_name.__name__} with id {id}')

    if (update_count == len(old_instances_list)) and update_count != 0:
        logger.info(f'All old instances in {related_model_name.__name__} are updated (update count: {len(old_instances_list)})')

    return data_list

# def validate_put_method_data(self, valid_data, serializer_name, update_fields, model_class_name, current_model_pk_field=None, using_db='default'):
#     error_list = []

#     if valid_data:
#         if isinstance(valid_data, list):
#             valid_data = valid_data
#         if isinstance(valid_data, dict):
#             valid_data = [valid_data]

#     for data in valid_data:
#         id = data.get(current_model_pk_field, None)
#         if id is not None:
#             instance = model_class_name.objects.using(using_db).filter(pk=id).first()
#             serializer = serializer_name(instance, data=data)
#             if not serializer.is_valid(raise_exception=False):
#                 error = serializer.errors
#                 model = serializer.Meta.model
#                 model_name = model.__name__
#                 logger.error("Validation error on %s: %s", model_name, str(error))
#                 error_list.append(error)
#         else:
#             serializer = serializer_name(data=data)
#             if not serializer.is_valid(raise_exception=False):
#                 error = serializer.errors
#                 exclude_keys = update_fields
#                 filtered_data = {k: v for k, v in error.items() if k not in exclude_keys}
#                 if filtered_data:
#                     error_list.append(filtered_data)

#     return error_list

def validate_put_method_data(self, valid_data, serializer_name, update_fields, model_class_name, current_model_pk_field=None, db_to_use=None):
    error_list = []
    
    #  Prioritize `db_to_use` if given, fallback to `using_db`
    selected_db = db_to_use

    if valid_data:
        if isinstance(valid_data, list):
            valid_data = valid_data
        if isinstance(valid_data, dict):
            valid_data = [valid_data]

    for data in valid_data:
        instance = None
        id = data.get(current_model_pk_field)
        if id is not None:
            instance = model_class_name.objects.using(selected_db).filter(pk=id).first()
            serializer = serializer_name(instance, data=data)
            if not serializer.is_valid(raise_exception=False):
                error = serializer.errors
                model = serializer.Meta.model
                model_name = model.__name__
                logger.error("Validation error on %s: %s", model_name, str(error))
                error_list.append(error)
        else:
            serializer = serializer_name(data=data)
            if not serializer.is_valid(raise_exception=False):
                error = serializer.errors
                exclude_keys = update_fields
                filtered_data = {k: v for k, v in error.items() if k not in exclude_keys}
                if filtered_data:
                    error_list.append(filtered_data)

    return error_list


# def update_multi_instances(self, pk, valid_data, related_model_name, related_class_name, update_fields, main_model_related_field=None, current_model_pk_field=None):
#     '''
#     related_model_class : name of the current model Name
#     main_model_related_field : This field should have the relation with main Model
#     '''
#     data_list = []
#     try:
#         filter_kwargs = {main_model_related_field:pk}
#         old_instances_list  = list(related_model_name.objects.filter(**filter_kwargs).values_list('pk', flat=True))
#         old_instances_list = [str(uuid) for uuid in old_instances_list] # conversion 
#     except Exception as e:
#         logger.error(f"Error fetching instances from {related_model_name.__name__}: {str(e)}")

#     # get the ids that are updated
#     pks_in_update_data = []

#     # prepare user provided pks and verify with the previous records
#     if valid_data:
#         if isinstance(valid_data, list):
#             valid_data = valid_data
#         if isinstance(valid_data, dict):
#             valid_data = [valid_data]

#     update_count = 0
#     for data in valid_data:
#         id = data.get(current_model_pk_field,None) # get the primary key in updated data
#         # update the data for avilable pks
#         if id is not None:
#             pks_in_update_data.append(id) # collecting how many ids are updated
#             instance = related_model_name.objects.get(pk=id)
#             # if given pk is avilable in old instances then update
#             if id in old_instances_list:
#                 serializer = related_class_name(instance, data=data, partial=False)
#                 serializer.is_valid(raise_exception=True)
#                 serializer.save()
#                 data_list.append(serializer.data)
#                 update_count = update_count + 1
#         # If there is no pk avilabe (id will be None), it is new record to create
#         else:
#             # create new record by using function 'generic_data_creation'
#             new_instance = generic_data_creation(self,[data],related_class_name,update_fields=update_fields)
#             if new_instance:
#                 data_list.append(new_instance[0]) # append the new record to existing records
#                 logger.info(f'New instance in {related_model_name.__name__} is created')
#             else:
#                 logger.warning("Error during update: new record creation failed in {related_model_name.__name__}")
#                 return build_response(0,f"Error during update: new record creation failed in {related_model_name.__name__}",[],status.HTTP_400_BAD_REQUEST)
            
#     # Delete the previous records if those are not mentioned in update data
#     for id in old_instances_list:
#         if id not in pks_in_update_data:
#             try:
#                 instance = related_model_name.objects.get(pk=id)
#                 instance.delete()
#                 logger.info(f'Old record in {related_model_name.__name__} with id {id} is deleted')
#             except Exception as e:
#                 logger.warning(f'Error deleting the record in {related_model_name.__name__} with id {id}')
  
#     if (update_count == len(old_instances_list)) and update_count != 0:
#         logger.info(f'All old instances in {related_model_name.__name__} are updated (update count : {len(old_instances_list)})')

#     return data_list

# def validate_put_method_data(self, valid_data, serializer_name, update_fields, model_class_name, current_model_pk_field=None):

#     error_list = []

#     if valid_data:
#         if isinstance(valid_data, list):
#             valid_data = valid_data
#         if isinstance(valid_data, dict):
#             valid_data = [valid_data]

#     for data in valid_data:
#         id = data.get(current_model_pk_field,None) # get the primary key in updated data
#         # update the data for avilable pks
#         if id is not None:
#             instance = model_class_name.objects.filter(pk=id).first()
#             serializer = serializer_name(instance,data=data)
#             # If Main model data is not valid
#             if not serializer.is_valid(raise_exception=False):
#                 error = serializer.errors
#                 model = serializer.Meta.model
#                 model_name = model.__name__
#                 logger.error("Validation error on %s: %s",model_name, str(error))  # Log validation error
#                 error_list.append(error)

#         # If there is no pk avilabe (id will be None), validate the new record
#         else:
#             serializer = serializer_name(data=data)
#             if not serializer.is_valid(raise_exception=False):
#                 error = serializer.errors
#                 exclude_keys = update_fields
#                 # Create a new dictionary excluding specified keys
#                 filtered_data = {k: v for k, v in error.items() if k not in exclude_keys}
#                 if filtered_data:
#                     error_list.append(filtered_data)

#     return error_list

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

def get_related_data(model, serializer_class, filter_field, filter_value):
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

def product_stock_verification(parent_model, child_model, data):
    """
    Verifies if sufficient stock is available for the product when a Sale/Purchase/work Order is being created.
    Raises a ValidationError if the product's available stock is less than the quantity being ordered.
    """
    def assign_error(balance, order_qty, stock_error, product, size=None, color=None):
        # Ensure balance is an integer and order_qty is also an integer
        from apps.products.models import Products, Size, Color
        product_name = Products.objects.get(product_id=product).name
        if balance <= 0:
            stock_error[f'{product_name}'] = f"Product is Out Of Stock. Available: {balance}, Ordered: {order_qty}"

        # Validate if the order_qty is greater than the available stock balance
        elif int(order_qty) > balance:
            stock_error[f'{product_name}'] = f'Insufficient stock for this product. Available: {balance}, Ordered: {order_qty}'

        # Product variation verification.
        try:
            if size or color: # if both are none, then it is direct product.
            # Update each product variation stock (Subtract/Add the order QTY from stock)
                product_variation_instance = child_model.objects.get(product_id=product, size_id=size, color_id=color)
        except Exception:
            size_name = (Size.objects.filter(size_id=size).first().size_name if size else None)
            color_name = (Color.objects.filter(color_id=color).first().color_name if color else None)
            logger.error(f"Product variation with size :{size_name} , color :{color_name} does not exist.")
            stock_error[f'{product_name}'] = f"Product variation with size :{size_name} , color :{color_name} does not exist."
    
    stock_error = {}
    
    for item in data:
        product = item.get('product_id', None)
        size = item.get('size_id', None)
        color = item.get('color_id', None)
        order_qty = item.get('quantity', None)

        try:
            # Verify if product has variations
            variations = child_model.objects.filter(product_id=product)
            if not variations.exists():  # Check if variations are not present
                # Verify the Main Product (Direct Product)
                product_balance = parent_model.objects.get(product_id=product).balance
                logger.info('product_balance = %s', product_balance)
                
                # Call the error handling function if stock is insufficient
                assign_error(product_balance, order_qty, stock_error, product, size, color)

            else:
                # Get the product variation (assuming only one variation exists for the combination)
                product_variation = child_model.objects.get(
                    product_id=product,
                    size_id=size,
                    color_id=color
                )
                
                # Validate the variation quantity
                assign_error(product_variation.quantity, order_qty, stock_error, product, size, color)

        except parent_model.DoesNotExist:
            logger.error(f'Product with ID {product} not found in Products model.')
        except child_model.DoesNotExist:
            assign_error(0, order_qty, stock_error, product, size, color)
            logger.error(f'Variation with product_id {product}, size_id {size}, color_id {color} not found in Product Variations.')
        except Exception as e:
            logger.error(f'Unexpected error: {str(e)}')

    return stock_error

def previous_product_instance_verification(model_name, data): # In case of Product Return
    """
    Verifies if PREVIOUS PRODUCT INTANCE is available for the product when a SaleOrder is was created.
    Raises a ValidationError if the product's instance is not present in database.
    """    
    stock_error = {}
    for item in data:
        product = item.get('product_id',None)
        size = item.get('size_id',None)
        color = item.get('color_id',None)
        order_qty = item.get('quantity',None)

        # Verify if 'Product variations' are present with provided 'product_id' in payload.
        product_variation_instance = model_name.objects.filter(product_id=product).exists()

        if product_variation_instance:
            # Verify the Product Varition
            try:
                product_variation = model_name.objects.get(
                    product_id=product,
                    size_id=size,
                    color_id=color
                )
                available_stock = product_variation.quantity
            except model_name.DoesNotExist:
                stock_error[f'{product}'] = 'This product variation is unavailable or has been removed.'
    return stock_error

# @transaction.atomic
# def update_product_stock(parent_model, child_model, data, operation):
#     for item in data:
#         product = item.get('product_id',None)
#         return_qty = int(item.get('quantity',None))
#         size = item.get('size_id',None)
#         color = item.get('color_id',None)

#         # Update each product stock (Subtract the order QTY from stock)
#         product_instance = parent_model.objects.get(product_id=product)
#         if operation == 'add':
#             product_instance.balance += return_qty
#         elif operation == 'subtract':
#             product_instance.balance -= return_qty
#         product_instance.save()

#         try:
#             # Update each product variation stock (Subtract/Add the order QTY from stock)
#             product_variation_instance = child_model.objects.get(
#                 product_id=product,
#                 size_id=size,
#                 color_id=color
#             )
#             if operation == 'add':
#                 product_variation_instance.quantity += return_qty
#             elif operation == 'subtract':
#                 product_variation_instance.quantity -= return_qty
#             product_variation_instance.save()
#             logger.info(f'Updated stock for Product ID : {product}')
#         except Exception:
#             logger.info('Direct Product stock is updated.')

# @transaction.atomic
# def update_product_stock(parent_model, child_model, data, operation, using='default'):
#     for item in data:
#         product = item.get('product_id', None)
#         return_qty = float(item.get('quantity', None))
#         size = item.get('size_id', None)
#         color = item.get('color_id', None)

#         # Update each product stock (Subtract the order QTY from stock)
#         product_instance = parent_model.objects.using(using).get(product_id=product)
#         if operation == 'add':
#             product_instance.balance += return_qty
#         elif operation == 'subtract':
#             product_instance.balance -= return_qty
#         product_instance.save(using=using)  #  respect DB

#         try:
#             # Update each product variation stock (Subtract/Add the order QTY from stock)
#             product_variation_instance = child_model.objects.using(using).get(
#                 product_id=product,
#                 size_id=size,
#                 color_id=color
#             )
#             if operation == 'add':
#                 product_variation_instance.quantity += return_qty
#             elif operation == 'subtract':
#                 product_variation_instance.quantity -= return_qty
#             product_variation_instance.save(using=using)  #  respect DB
#             logger.info(f'Updated stock for Product ID : {product}')
#         except Exception:
#             logger.info('Direct Product stock is updated.')

@transaction.atomic
def update_product_stock(parent_model, child_model, data, operation, using='default'):
    for item in data:
        product_id = item.get('product_id')
        return_qty = float(item.get('quantity', 0))
        size_id = item.get('size_id')
        color_id = item.get('color_id')

        try:
            with transaction.atomic(using=using):
                # Update parent product
                product_instance = parent_model.objects.using(using).select_for_update().get(product_id=product_id)
                
                if operation == 'add':
                    product_instance.balance += return_qty
                elif operation == 'subtract':
                    product_instance.balance -= return_qty
                product_instance.save(using=using)

                # Update or create variation if size/color provided
                if size_id and color_id:
                    variation, created = child_model.objects.using(using).get_or_create(
                        product_id=product_id,
                        size_id=size_id,
                        color_id=color_id,
                        defaults={'quantity': return_qty if operation == 'add' else -return_qty}
                    )
                    
                    if not created:
                        if operation == 'add':
                            variation.quantity += return_qty
                        elif operation == 'subtract':
                            variation.quantity -= return_qty
                        variation.save(using=using)
                        
                    logger.info(f'{"Created" if created else "Updated"} variation for Product ID: {product_id}')
                
        except parent_model.DoesNotExist:
            logger.error(f'Product with ID {product_id} does not exist')
        except Exception as e:
            logger.error(f'Error updating stock for Product ID {product_id}: {e}')
            raise  # Re-raise to maintain transaction integrity

#=========================== COMMUNICATION / REPORTS / OTHER SPECIAL FUNCTIONS (CHETAN) ============================

def remove_fields(obj):
    """
    It removes fields from role_permissions for sending Proper data to frontend team after successfully login
    """
    if isinstance(obj, dict):
        obj.pop('created_at', None)
        obj.pop('updated_at', None)
        for value in obj.values():
            remove_fields(value)
    elif isinstance(obj, list):
        for item in obj:
            remove_fields(item)

def validate_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        raise ValidationError("Invalid UUID")
    return uuid_obj
     
def format_phone_number(phone_number):
    phone_number_str = str(phone_number) 
    
    # Check if the phone number length is correct
    if len(phone_number_str) == 10:
        return "91" + phone_number_str  #
    elif len(phone_number_str) == 12 and phone_number_str.startswith("91"):
        return phone_number_str  
    else:
        return "N/A"  

# def send_pdf_via_email(to_email, pdf_relative_path):
#     """Send the generated PDF as an email attachment."""
    
#     # Construct the full path to the PDF file
#     pdf_full_path = os.path.join(MEDIA_ROOT, pdf_relative_path)
    
#     subject = 'Your Requested Documents'
#     body = 'Please Find Your Requested Documents.'
#     email = EmailMessage(subject, body, to=[to_email])

#     # Ensure the PDF file exists before attempting to open it
#     if not os.path.exists(pdf_full_path):
#         raise FileNotFoundError(f"The file {pdf_full_path} does not exist.")

#     # Read the PDF file from the provided full path
#     with open(pdf_full_path, 'rb') as pdf_file:
#         email.attach('Document.pdf', pdf_file.read(), 'application/pdf')
    
#     # Send the email
#     email.send()

#     return "PDF sent via Email successfully."

import os
from django.core.mail import EmailMessage

def send_pdf_via_email(to_email, pdf_relative_path, document_type):
    """Send the generated PDF as an email attachment based on the document type."""

    # Construct the full path to the PDF file
    pdf_full_path = os.path.join(MEDIA_ROOT, pdf_relative_path)

    # Define subject and body based on document type
    doc_messages = {
        "sale_order": ("Sale Order Document", "Please Find Your Requested Sale Order Documents."),
        "sale_quotation": ("Sale Quotation Document", "Please Find Your Requested Sale Quotation Documents."),
        "sale_invoice": ("Sale Invoice Document", "Please Find Your Requested Sale Invoice Documents."),
        "sale_return": ("Sale Return Document", "Please Find Your Requested Sale Return Documents."),
        "purchase_order": ("Purchase Order Document", "Please Find Your Requested Purchase Order Documents."),
        "purchase_return": ("Purchase Return Document", "Please Find Your Requested Purchase Return Documents."),
        "payment_receipt": ("Payment Receipt Document", "Please Find Your Requested Payment Receipt Documents."), #payment_receipt
    }

    subject, body = doc_messages.get(document_type, ("Your Requested Documents", "Please Find Your Requested Documents."))

    email = EmailMessage(subject, body, to=[to_email])

    # Ensure the PDF file exists before attempting to open it
    if not os.path.exists(pdf_full_path):
        raise FileNotFoundError(f"The file {pdf_full_path} does not exist.")

    # Read the PDF file from the provided full path
    with open(pdf_full_path, 'rb') as pdf_file:
        email.attach('Document.pdf', pdf_file.read(), 'application/pdf')

    # Send the email
    email.send()

    return f"{document_type.replace('_', ' ').title()} PDF sent via Email successfully."



def send_whatsapp_message_via_wati(to_number, file_url):
    """ Send the PDF file as a WhatsApp message using WATI API. """
    result = ""
    # Construct the full path to the file using MEDIA_ROOT
    full_file_path = os.path.join(MEDIA_ROOT, file_url.replace(MEDIA_URL, ''))
    # Ensure the file exists
    if not os.path.exists(full_file_path):
        return (f"File not found: {full_file_path}")            
    
    url = f'https://live-mt-server.wati.io/312172/api/v1/sendSessionFile/{to_number}'
    
    headers = {
    'accept': '*/*',
    'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJlMzMyNWFmNC0wNDE2LTQzYTQtOTcwNi00MGYxZDViZTM0MGQiLCJ1bmlxdWVfbmFtZSI6InJ1ZGhyYWluZHVzdHJpZXMubmxyQGdtYWlsLmNvbSIsIm5hbWVpZCI6InJ1ZGhyYWluZHVzdHJpZXMubmxyQGdtYWlsLmNvbSIsImVtYWlsIjoicnVkaHJhaW5kdXN0cmllcy5ubHJAZ21haWwuY29tIiwiYXV0aF90aW1lIjoiMDgvMjYvMjAyNCAwNjowMzozNSIsImRiX25hbWUiOiJtdC1wcm9kLVRlbmFudHMiLCJ0ZW5hbnRfaWQiOiIzMTIxNzIiLCJodHRwOi8vc2NoZW1hcy5taWNyb3NvZnQuY29tL3dzLzIwMDgvMDYvaWRlbnRpdHkvY2xhaW1zL3JvbGUiOiJBRE1JTklTVFJBVE9SIiwiZXhwIjoyNTM0MDIzMDA4MDAsImlzcyI6IkNsYXJlX0FJIiwiYXVkIjoiQ2xhcmVfQUkifQ.qFA42Ze-itghM2LXR5sZ-P9BJB84iD3oXqk5olG_kX8',
    }

    # Open the file and attach it to the request
    with open(full_file_path, 'rb') as file:
        files = {
            'file': (os.path.basename(full_file_path), file, 'application/pdf'),
        }
        response = requests.post(url, headers=headers, files=files)

        # Convert the response text to a Python dictionary
    response_data = json.loads(response.text) 

    if response_data.get("result") == True:
        result = "PDF sent via WhatsApp successfully."
        return result
    else:
        result = response_data.get('info')
        return result

def convert_amount_to_words(amount):
    '''
This Code convert amount into world.
Ex. amount = 784365923.04
    O/P = INR Seventy-Eight Crore Forty-Three Lakh Sixty-Five Thousand Nine Hundred Twenty-Three And Four Paise
-------------For Testing---------------
# # Example usage:
# amount = 784365923.04
# result = convert_amount_to_words(amount)
# print((result))  

'''
    # Split amount into rupees and paise
    amount_parts = str(amount).split(".")
    
    # Convert rupees part
    rupees_part = int(amount_parts[0])
    
    # Check if there are paise
    paise_part = int(amount_parts[1]) if len(amount_parts) > 1 else 0
    
    # Convert rupees to words
    rupees_in_words = convert_rupees_to_indian_words(rupees_part)
    
    # Convert paise to words
    p = inflect.engine()
    paise_in_words = (
        p.number_to_words(paise_part).replace(",", "") if paise_part > 0 else "zero"
    )
    
    amt_world = f"{rupees_in_words} and {paise_in_words} paise"
    return "INR " + amt_world.title() 

def convert_rupees_to_indian_words(number):
    p = inflect.engine()
    if number == 0:
        return "zero rupees"
    
    parts = []
    
    # Define thresholds and labels
    units = [
        (1000000000, "arab"),
        (10000000, "crore"),
        (100000, "lakh"),
        (1000, "thousand"),
        (100, "hundred")
    ]
    
    for value, name in units:
        if number >= value:
            quotient, number = divmod(number, value)
            parts.append(f"{p.number_to_words(quotient)} {name}")
    
    if number > 0:
        parts.append(p.number_to_words(number))
    
    return " ".join(parts)

def extract_product_data(data, tax_type=None):
    product_data = []
    
    for index, item in enumerate(data, start=1):
        product = item['product']
        unit_options = item['unit_options']        
        product_name = product['name']
        total_boxes = item['total_boxes']
        quantity = float(item['quantity'])
        unit_name = unit_options['unit_name']
        rate = float(item['rate'])
        amount = float(quantity * rate)
        discount_percent = item['discount']
        discount = quantity * rate * float(discount_percent) / 100      
        total_amount = float(item['amount'])

        cgst = float(item['cgst'])
        sgst = float(item['sgst'])
        igst = float(item['igst'])
        gst_tax = 0.0 if tax_type == 'Inclusive' else float(cgst + sgst + igst)

        product_data.append([
            index, product_name, total_boxes, quantity, unit_name, rate, amount, discount_percent, discount, gst_tax, total_amount
        ])

    return product_data


# def extract_product_data(data):
#     product_data = []
    
#     for index, item in enumerate(data, start=1):
#         product = item['product']
#         unit_options = item['unit_options']        
#         product_name = product['name']
#         total_boxes = item['total_boxes']
#         quantity = float(item['quantity'])#item['quantity']
#         unit_name = unit_options['unit_name']
#         rate = float(item['rate']) #item['rate']
#         amount = float(quantity * rate)
#         discount_percent = item['discount']  # Convert discount to float
#         discount = quantity * rate * float(item['discount']) / 100  # Convert discount to float      
#         total_amount = float(item['amount'])  # Convert to float
#         cgst = float(item['cgst'])
#         sgst = float(item['sgst'])
#         igst = float(item['igst'])
#         gst_tax = float(cgst + sgst + igst)
        
#         product_data.append([
#             index, product_name, total_boxes, quantity, unit_name, rate, amount, discount_percent, discount, gst_tax, total_amount ])

#     return product_data

def path_generate(document_type):
    # Generate a random filename
    unique_code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=4)) + '.pdf'
    doc_name = document_type + '_' + unique_code
    # Construct the full file path
    file_path = os.path.join(settings.MEDIA_ROOT, 'doc_generater', doc_name)
    # Ensure that the directory exists
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Return the relative path to the file (relative to MEDIA_ROOT)
    relative_file_path = os.path.join('doc_generater', os.path.basename(doc_name))
    # cdn_path = os.path.join(MEDIA_URL, relative_file_path)
    # print(cdn_path)

    return doc_name, file_path, relative_file_path

#workflow code
workflow_progression_dict = {}
def get_section_id(section_name):
    """
    Retrieve the section ID from the ModuleSections model based on the provided section name.
    This function can be used for any module by passing the appropriate section name (e.g., 'Sale Order', 'Purchase Order').
    """
    from apps.users.models import ModuleSections

    try:
        # Look up the section based on the given section name
        section = ModuleSections.objects.filter(section_name=section_name).first()
        if section:
            return section.section_id
        else:
            raise ValueError(f"Section '{section_name}' not found in ModuleSections")
    except Exception as e:
        raise ValueError(f"Error fetching section_id for {section_name}: {str(e)}")

#Added new logic
def get_active_workflow(section_id):
    """
    Retrieve the active workflow based on the given section_id by looking up the WorkflowStage.
    """
    from apps.sales.models import Workflow, WorkflowStage
    try:
        # Step 1: Find the active workflow for the section by checking WorkflowStage for a match
        active_workflow = Workflow.objects.filter(is_active=True, workflowstage__section_id=section_id).first()

        if not active_workflow:
            raise ValueError(f"No active workflow found for section_id {section_id}")

        print(f"Active Workflow ID: {active_workflow.workflow_id}")

        # Step 2: Retrieve the first stage of this active workflow
        first_stage = WorkflowStage.objects.filter(
            workflow_id=active_workflow.workflow_id, section_id=section_id
        ).order_by('stage_order').first()

        if first_stage:
            return active_workflow
        else:
            raise ValueError(f"No stages found for active workflow with ID {active_workflow.workflow_id}")

    except Exception as e:
        raise ValueError(f"Error fetching active workflow: {str(e)}")

class IsAdminRoles(BasePermission):
    """
    Custom permission to allow access only to users with the 'Admin' role.

    This checks the authenticated user's associated role via the `role_id` ForeignKey
    and ensures that the role's `name` field is equal to "Admin".

    Returns: True if the user is authenticated and their role is 'Admin', False otherwise.
    """
    def has_permission(self, request, view):
        user = request.user
        return (
            user.is_authenticated and 
            hasattr(user, 'role_id') and 
            getattr(user.role_id, 'role_name', '').lower() == "admin"
        )
    

class BaseExcelImportExport:
    """
    Base class for Excel import/export functionality that can be reused across different models.
    This class provides a foundation for Excel template generation, file upload, validation,
    and data import across different components in the application.
    
    Usage:
        1. Create a subclass for your specific model (e.g., CustomerExcelImport)
        2. Override the class attributes (MODEL_CLASS, FIELD_MAP, etc.)
        3. Implement the create_record method
        4. Set up API views that use your subclass
    """
    # Override these in child classes
    MODEL_CLASS = None
    SERIALIZER_CLASS = None
    REQUIRED_COLUMNS = []
    FIELD_MAP = {}
    BOOLEAN_FIELDS = []
    LOOKUP_FIELDS = {}  # Maps foreign keys to their lookup models
    TEMPLATE_FILENAME = "Export_Template.xlsx"
    
    @classmethod
    def generate_template(cls, extra_columns=None):
        """
        Generate an Excel template for the model
        
        Args:
            extra_columns: Additional columns to include in the template
            
        Returns:
            Openpyxl workbook object
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "ImportTemplate"
        
        # Get all fields from FIELD_MAP
        headers = list(cls.FIELD_MAP.keys())
        
        # Add extra columns if provided
        if extra_columns:
            headers.extend(extra_columns)
        
        # Add headers to worksheet
        ws.append(headers)
        
        # Style headers
        header_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
        font_bold = Font(bold=True)
        align_center = Alignment(horizontal="center")
        
        for col_num, column_title in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = font_bold
            cell.alignment = align_center
            
            # Mark required fields
            if column_title in cls.REQUIRED_COLUMNS:
                cell.comment = Comment("This field is required", "System")
            
            # Set column width
            ws.column_dimensions[get_column_letter(col_num)].width = len(str(column_title)) + 4
        
        return wb
        
    @classmethod
    def get_template_response(cls, request, extra_columns=None):
        """
        Generates an Excel template with headers based on FIELD_MAP and extra_columns.
        
        Args:
            request: HTTP request object
            extra_columns: Additional columns to include in the template
            
        Returns:
            HttpResponse with Excel file attachment
        """
        wb = cls.generate_template(extra_columns)
        
        # Create and return the response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={cls.TEMPLATE_FILENAME}'
        wb.save(response)
        return response

    @classmethod
    def save_upload(cls, file):
        """Save the uploaded file to disk"""
        upload_dir = 'media/uploads'
        os.makedirs(upload_dir, exist_ok=True)
        
        file_path = os.path.join(upload_dir, file.name)
        with open(file_path, 'wb+') as dest:
            for chunk in file.chunks():
                dest.write(chunk)
        return file_path

    @classmethod
    def process_excel_file(cls, file, create_record_func, get_or_create_funcs=None):
        """Process the uploaded Excel file and import records."""
        if not file:
            return {"error": "No file uploaded"}, status.HTTP_400_BAD_REQUEST
        
        # Check file type
        file_name = file.name.lower()
        if not (file_name.endswith('.xlsx') or file_name.endswith('.xls')):
            return {"error": "Invalid file format. Only Excel files (.xlsx or .xls) are supported."}, status.HTTP_400_BAD_REQUEST
        
        # Save and process the file
        file_path = cls.save_upload(file)
        
        try:
            # Load the workbook
            wb = openpyxl.load_workbook(file_path)
            sheet = wb.active
            
            # Get headers from first row
            headers = [str(cell.value).lower() if cell.value else "" for cell in sheet[1]]
            
            # Validate required columns
            missing_columns = []
            for col in cls.REQUIRED_COLUMNS:
                if col.lower() not in headers:
                    missing_columns.append(col)
            
            if missing_columns:
                return {
                    "error": "Excel template format mismatch. Required columns are missing.",
                    "missing_columns": missing_columns,
                }, status.HTTP_400_BAD_REQUEST
            
            # Get ALL valid columns - including any additional headers defined in child classes
            all_expected_columns = list(cls.FIELD_MAP.keys())
            
            # Add additional special headers from any class-specific header collections
            special_header_attributes = [attr for attr in dir(cls) if attr.endswith('_HEADERS') and attr != 'REQUIRED_COLUMNS']
            for attr in special_header_attributes:
                if hasattr(cls, attr):
                    additional_headers = getattr(cls, attr)
                    if isinstance(additional_headers, list):
                        all_expected_columns.extend(additional_headers)
            
            # Also allow address-related fields with billing_ or shipping_ prefixes
            # Check for columns in Excel that are not in our expected list
            unexpected_columns = []
            for header in headers:
                if header and header not in [col.lower() for col in all_expected_columns] and not header.startswith('billing_') and not header.startswith('shipping_'):
                    unexpected_columns.append(header)
            
            # Check for expected columns that are missing from Excel (only from FIELD_MAP, not additional headers)
            missing_expected_columns = []
            for expected_col in cls.FIELD_MAP.keys():  # Only check main fields, not additional headers
                if expected_col.lower() not in headers:
                    missing_expected_columns.append(expected_col)
            
            if unexpected_columns or missing_expected_columns:
                return {
                    "error": "Excel template format mismatch.",
                    "unexpected_columns": unexpected_columns,
                    "missing_expected_columns": missing_expected_columns,
                }, status.HTTP_400_BAD_REQUEST
            
            # Extract data rows
            data_rows = []
            for row in list(sheet.iter_rows(min_row=2, values_only=True)):
                if any(cell is not None for cell in row):
                    data_rows.append(row)
            
            # Check for missing required data
            missing_data_rows = []
            for idx, row in enumerate(data_rows, start=2):
                row_data = dict(zip(headers, row))
                missing_fields = []
                
                for field in cls.REQUIRED_COLUMNS:
                    if field.lower() in headers and not row_data.get(field.lower()):
                        missing_fields.append(field)
                
                if missing_fields:
                    missing_data_rows.append({
                        "row": idx,
                        "missing_fields": missing_fields
                    })
            
            if missing_data_rows:
                return {
                    "error": "Some rows are missing required data.",
                    "missing_data_rows": missing_data_rows
                }, status.HTTP_400_BAD_REQUEST
            
            # Process valid rows
            results = cls.process_rows(headers, data_rows, create_record_func, get_or_create_funcs)
            return results, status.HTTP_200_OK
            
        except Exception as e:
            logger.error(f"Error processing Excel file: {str(e)}")
            return {"error": f"Error processing Excel file: {str(e)}"}, status.HTTP_400_BAD_REQUEST
    
    @classmethod
    def process_rows(cls, headers, data_rows, create_record_func, get_or_create_funcs=None):
        """Process all rows from Excel file"""
        success = 0
        failed = []
        
        for idx, row in enumerate(data_rows, start=2):
            row_data = dict(zip(headers, row))
            
            # Check all required fields
            missing_fields = []
            for field in cls.REQUIRED_COLUMNS:
                if not row_data.get(field):
                    missing_fields.append(field)
            
            if missing_fields:
                failed.append({
                    "row": idx, 
                    "error": f"Missing required fields: {', '.join(missing_fields)}"
                })
                continue
                
            try:
                with transaction.atomic():
                    # Use the provided function to create the record
                    create_record_func(row_data, cls.FIELD_MAP, cls.BOOLEAN_FIELDS, get_or_create_funcs)
                    
                success += 1
                    
            except Exception as e:
                logger.error(f"Error processing row {idx}: {e}")
                failed.append({"row": idx, "error": str(e)})
                
        return {
            "message": f"{success} records imported successfully.",
            "errors": failed
        }
    
    @staticmethod
    def parse_boolean(value):
        """Convert various formats to boolean"""
        if value is None:
            return None
            
        value_str = str(value).strip().lower()
        if value_str in ["yes", "true", "1"]:
            return True
        elif value_str in ["no", "false", "0"]:
            return False
            
        return None
        
    @classmethod
    def create_record(cls, row_data, field_map=None, boolean_fields=None, get_or_create_funcs=None):
        """
        Creates a record from row data.
        This method should be implemented by subclasses to handle specific model creation.
        
        Args:
            row_data: Dictionary mapping column names to values
            field_map: Dictionary mapping Excel column names to model fields
            boolean_fields: List of fields that should be treated as boolean
            get_or_create_funcs: Dictionary of functions to get or create related objects
            
        Returns:
            Created model instance
        """
        raise NotImplementedError("Subclasses must implement create_record method")
        
    @classmethod
    def get_or_create_fk(cls, model, value, field="name"):
        """Get or create a foreign key reference"""
        if not value:
            return None
            
        value = str(value).strip()
        obj = model.objects.filter(**{f"{field}__iexact": value}).first()
        
        if obj:
            return obj
            
        logger.info(f"Creating {model.__name__} with {field}='{value}'")
        
        # Special case handling for models with required fields
        if hasattr(cls, 'FK_REQUIRED_FIELDS') and model.__name__ in cls.FK_REQUIRED_FIELDS:
            required_fields = cls.FK_REQUIRED_FIELDS[model.__name__]
            create_data = {field: value}
            
            for req_field, default_provider in required_fields.items():
                if callable(default_provider):
                    create_data[req_field] = default_provider()
                else:
                    create_data[req_field] = default_provider
                    
            return model.objects.create(**create_data)
        
        # Standard case - just create with the name field
        return model.objects.create(**{field: value})
    
    @classmethod
    def generate_template(cls, extra_columns=None):
        """
        Generate an Excel template for the model
        
        Args:
            extra_columns: Additional columns to include in the template
            
        Returns:
            Openpyxl workbook object
        """
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = "ImportTemplate"
        
        # Get all fields from FIELD_MAP
        headers = list(cls.FIELD_MAP.keys())
        
        # Add extra columns if provided
        if extra_columns:
            headers.extend(extra_columns)
        
        # Add headers to worksheet
        ws.append(headers)
        
        # Style headers
        header_fill = PatternFill(start_color="ADD8E6", end_color="ADD8E6", fill_type="solid")
        font_bold = Font(bold=True)
        align_center = Alignment(horizontal="center")
        
        for col_num, column_title in enumerate(headers, 1):
            cell = ws.cell(row=1, column=col_num)
            cell.fill = header_fill
            cell.font = font_bold
            cell.alignment = align_center
            
            # Mark required fields
            if column_title in cls.REQUIRED_COLUMNS:
                cell.comment = Comment("This field is required", "System")
            
            # Set column width
            ws.column_dimensions[get_column_letter(col_num)].width = len(str(column_title)) + 4
        
        return wb
        
    @classmethod
    def get_template_response(cls, request, extra_columns=None):
        """
        Generates an Excel template with headers based on FIELD_MAP and extra_columns.
        
        Args:
            request: HTTP request object
            extra_columns: Additional columns to include in the template
            
        Returns:
            HttpResponse with Excel file attachment
        """
        wb = cls.generate_template(extra_columns)
        
        # Create and return the response
        response = HttpResponse(
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        response['Content-Disposition'] = f'attachment; filename={cls.TEMPLATE_FILENAME}'
        wb.save(response)
        return response

    @classmethod
    def upload_file(cls, request):
        """
        Handle file upload for Excel import.
        
        Args:
            request: HTTP request object with file attachment
            
        Returns:
            Tuple: (file_path, status_code) or (error_response, status_code)
        """
        file = request.FILES.get('file')
        if not file:
            return {"error": "No file uploaded"}, status.HTTP_400_BAD_REQUEST
            
        # Check file type
        file_name = file.name.lower()
        if not (file_name.endswith('.xlsx') or file_name.endswith('.xls')):
            return {"error": "Invalid file format. Only Excel files (.xlsx or .xls) are supported."}, status.HTTP_400_BAD_REQUEST
            
        # Save and process the file
        return cls.save_upload(file), status.HTTP_200_OK
    

    
