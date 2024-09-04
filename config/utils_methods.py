#utils_methods file
import logging
# from django.forms import ValidationError
from rest_framework.serializers import ValidationError
from rest_framework.response import Response
from rest_framework import status
from django.db import models
import uuid
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
    if order_type_prefix == "PRD":
        key = f"{order_type_prefix}"
        sequence_number = cache.get(key, 0)
        sequence_number += 1
        cache.set(key, sequence_number, timeout=None)

        sequence_number_str = f"{sequence_number:05d}"
        order_number = f"{order_type_prefix}-{sequence_number_str}"
    else:

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

        if bulk_data:
            if isinstance(bulk_data, list):
                bulk_data = bulk_data
            if isinstance(bulk_data, dict):
                bulk_data = [bulk_data]
        
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
    if valid_data:
        if isinstance(valid_data, list):
            valid_data = valid_data
        if isinstance(valid_data, dict):
            valid_data = [valid_data]

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
                logger.info(f'New instance in {related_model_name.__name__} is created')
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
  
    if (update_count == len(old_instances_list)) and update_count != 0:
        logger.info(f'All old instances in {related_model_name.__name__} are updated (update count : {len(old_instances_list)})')

    return data_list

def validate_put_method_data(self, valid_data, serializer_name, update_fields, model_class_name, current_model_pk_field=None):

    error_list = []

    if valid_data:
        if isinstance(valid_data, list):
            valid_data = valid_data
        if isinstance(valid_data, dict):
            valid_data = [valid_data]

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


#================================================================================================================================================
#===========================================CHETAN'S METHOD============================================================================
#================================================================================================================================================
def validate_uuid(uuid_to_test, version=4):
    try:
        uuid_obj = uuid.UUID(uuid_to_test, version=version)
    except ValueError:
        raise ValidationError("Invalid UUID")
    return uuid_obj


        

def get_related_data(model, serializer_class, filter_field, filter_value):
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

     
def format_phone_number(phone_number):
    phone_number_str = str(phone_number) 
    
    # Check if the phone number length is correct
    if len(phone_number_str) == 10:
        return "91" + phone_number_str  #
    elif len(phone_number_str) == 12 and phone_number_str.startswith("91"):
        return phone_number_str  
    else:
        return "Mobile number has incorrect length"  

from django.core.mail import EmailMessage
def send_pdf_via_email(to_email, pdf_relative_path):
    """Send the generated PDF as an email attachment."""
    
    # Construct the full path to the PDF file
    pdf_full_path = os.path.join(MEDIA_ROOT, pdf_relative_path)
    
    subject = 'Your Sales Order Receipt'
    body = 'Please find attached your sales order receipt.'
    email = EmailMessage(subject, body, to=[to_email])

    # Ensure the PDF file exists before attempting to open it
    if not os.path.exists(pdf_full_path):
        raise FileNotFoundError(f"The file {pdf_full_path} does not exist.")

    # Read the PDF file from the provided full path
    with open(pdf_full_path, 'rb') as pdf_file:
        email.attach('sales_order_receipt.pdf', pdf_file.read(), 'application/pdf')
    
    # Send the email
    email.send()

    return "PDF sent via Email successfully."


from config.settings import MEDIA_ROOT, MEDIA_URL
import requests

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

import os
import shutil
import inflect
from config.settings import MEDIA_ROOT
# from apps.sales.utils import sales_order_rcpt_word_docx as wd


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



def extract_product_data(data):
    product_data = []
    
    for index, item in enumerate(data, start=1):
        product = item['product']
        unit_options = item['unit_options']        
        product_name = product['name']
        quantity = item['quantity']
        unit_name = unit_options['unit_name']
        rate = item['rate']
        amount = item['amount']
        discount = item['discount']
        tax = (item['tax'] if item['tax'] is not None else 0)
        
        product_data.append([
            str(index), product_name, quantity, unit_name, rate, amount, discount, tax])

    return product_data


# def save_sales_order_pdf_to_media(product_data, cust_data):
#     # Generate the PDF file
#     pdf_file_path = wd.create_sales_order_doc(product_data, cust_data)
    
#     # Define the directory where the file will be saved
#     sales_order_dir = os.path.join(MEDIA_ROOT, 'sales order receipt')

#     # Create the directory if it doesn't exist
#     if not os.path.exists(sales_order_dir):
#         os.makedirs(sales_order_dir)

#     # Define the new file path in the media directory
#     new_file_path = os.path.join(sales_order_dir, os.path.basename(pdf_file_path))
    
#     # Move the PDF file to the new directory
#     shutil.move(pdf_file_path, new_file_path)

#     # Return the relative path to the file (relative to MEDIA_ROOT)
#     relative_file_path = os.path.join('sales order receipt', os.path.basename(pdf_file_path))
#     return relative_file_path