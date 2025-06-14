from rest_framework import viewsets
from apps.customfields.filters import CustomFieldFilter, CustomFieldOptionsFilters, CustomFieldValuesFilters
from config.utils_filter_methods import filter_response, list_filtered_objects
from config.utils_methods import create_instance, list_all_objects, list_all_objects_1, update_instance
from .models import CustomField, CustomFieldOption, CustomFieldValue
from .serializers import  CustomFieldSerializer, CustomFieldOptionSerializer, CustomFieldValueSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.db import transaction
from rest_framework.exceptions import ValidationError
from django.http import Http404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import OrderingFilter
import logging
from config.utils_methods import update_multi_instances, validate_input_pk, delete_multi_instance, build_response, validate_put_method_data, generic_data_creation
logger = logging.getLogger(__name__)

class CustomFieldViewSet(viewsets.ModelViewSet):
    queryset = CustomField.objects.all()
    serializer_class = CustomFieldSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CustomFieldFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, CustomField,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class CustomFieldOptionViewSet(viewsets.ModelViewSet):
    queryset = CustomFieldOption.objects.all()
    serializer_class = CustomFieldOptionSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CustomFieldOptionsFilters 

    def list(self, request, *args, **kwargs):
        return list_all_objects_1(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class CustomFieldValueViewSet(viewsets.ModelViewSet):
    queryset = CustomFieldValue.objects.all()
    serializer_class = CustomFieldValueSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = CustomFieldValuesFilters 

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class CustomFieldCreateViewSet(APIView):
    """
    API ViewSet for handling custom field creation and related options, similar to LeadsViewSet.
    """

    def get_object(self, pk):
        try:
            return CustomField.objects.get(pk=pk)
        except CustomField.DoesNotExist:
            logger.warning(f"CustomField with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(request, *args, **kwargs)

        try:
            logger.info("Retrieving all custom fields")

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10))

            queryset = CustomField.objects.all()

            # Apply filters manually
            if request.query_params:
                filterset = CustomFieldFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            total_count = CustomField.objects.count()

            serializer = CustomFieldSerializer(queryset, many=True)
            logger.info("Custom field data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a custom field and its related options.
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the CustomField instance
            custom_field = get_object_or_404(CustomField, pk=pk)
            custom_field_serializer = CustomFieldSerializer(custom_field)

            # Retrieve related CustomFieldOptions
            custom_field_options = self.get_related_data(CustomFieldOption, CustomFieldOptionSerializer, 'custom_field_id', pk)

            # Customizing the response data
            custom_data = {
                "custom_field": custom_field_serializer.data,
                "custom_field_options": custom_field_options
            }

            logger.info("CustomField and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        
        except Http404:
            logger.error("custom_field record with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.exception(f"An error occurred while retrieving custom field with pk {pk}: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    

    def get_related_data(self, model, serializer_class, filter_field, filter_value):
        """
        Retrieves related data for a given model, serializer, and filter field.
        """
        try:
            related_data = model.objects.filter(**{filter_field: filter_value})
            serializer = serializer_class(related_data, many=True)
            logger.debug(f"Retrieved related data for model {model.__name__} with filter {filter_field}={filter_value}.")
            return serializer.data
        except Exception as e:
            logger.exception(f"Error retrieving related data for model {model.__name__} with filter {filter_field}={filter_value}: {str(e)}")
            return []

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Handles the creation of custom fields and their associated options.
        """
        given_data = request.data

        # Extract custom field data
        custom_field_data = given_data.pop('custom_field', None)
        custom_field_options_data = given_data.pop('custom_field_options', [])

        # Validate presence of mandatory data
        if not custom_field_data:
            logger.error("Custom field data is mandatory but not provided.")
            return build_response(0, "Custom field data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        try:
            # Step 1: Create CustomField using serializer and catch all validation errors (uniqueness, foreign key, etc.)
            custom_field_serializer = CustomFieldSerializer(data=custom_field_data)
            custom_field_serializer.is_valid(raise_exception=True)  # Perform all validations at once
            custom_field = custom_field_serializer.save()  # Save the custom field
            custom_field_id = custom_field.custom_field_id  # Get the newly created custom field ID
            logger.info('CustomField created successfully.')

            # Step 2: Create CustomFieldOptions if provided
            if custom_field_options_data:
                # Link each option to the custom field
                for option_data in custom_field_options_data:
                    option_data['custom_field_id'] = custom_field_id

                custom_field_options = generic_data_creation(self, custom_field_options_data, CustomFieldOptionSerializer)
                logger.info('CustomFieldOptions created successfully.')

            custom_data = {
                "custom_field": custom_field_serializer.data,
                "custom_field_options": custom_field_options if custom_field_options_data else []
            }

            return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

        except ValidationError as e:
            # Return all validation errors at once, including invalid foreign key or uniqueness errors
            logger.error(f"Validation error: {e.detail}")
            return build_response(0, "ValidationError", e.detail, status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            # Catch any other exceptions
            logger.error(f"Error creating custom field and options: {str(e)}")
            return build_response(0, "Record creation failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


        except Exception as e:
            logger.error(f"Error creating custom field and options: {str(e)}")
            return build_response(0, "Record creation failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        """
        Handles the updating of custom fields and their associated options.
        """
        # Get the given data from request
        given_data = request.data

        # Initialize the error variable for custom_field_options
        options_error = None

        # Step 1: Extract and validate CustomField Data
        custom_field_data = given_data.pop('custom_field', None)
        if custom_field_data:
            custom_field_data['custom_field_id'] = pk  # Ensure we're updating the right record

            # Manually handle uniqueness validation (like in SaleOrder)
            existing_field = CustomField.objects.exclude(custom_field_id=pk).filter(
                field_name=custom_field_data.get('field_name'), 
                # entity_name=custom_field_data.get('entity_name')
            ).first()

            if existing_field:
                return build_response(0, "ValidationError", {
                    'custom_field': [
                        {
                            'field_name': ['Custom field with this field name already exists.'],
                            # 'entity_name': ['Custom field with this entity name already exists.']
                        }
                    ]
                }, status.HTTP_400_BAD_REQUEST)

        # Step 2: Extract and validate CustomFieldOptions Data
        custom_field_options_data = given_data.pop('custom_field_options', None)
        if custom_field_options_data:
            exclude_fields = ['custom_field_id']
            options_error = validate_put_method_data(self, custom_field_options_data, CustomFieldOptionSerializer,
                                                    exclude_fields, CustomFieldOption, current_model_pk_field='option_id')

        # Ensure mandatory data is present
        if not custom_field_data:
            logger.error("Custom field data is mandatory but not provided.")
            return build_response(0, "Custom field data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        # Initialize errors dictionary
        errors = {}
        
        # If there are errors from the options validation, add them
        if options_error:
            errors["custom_field_options"] = options_error

        # Return if any validation errors exist
        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # Step 3: Update CustomField
        custom_field_update = update_multi_instances(self, pk, [custom_field_data], CustomField, CustomFieldSerializer,
                                                    [], main_model_related_field='custom_field_id', current_model_pk_field='custom_field_id')

        # Step 4: Update CustomFieldOptions
        custom_field_options_update = update_multi_instances(self, pk, custom_field_options_data, CustomFieldOption,
                                                            CustomFieldOptionSerializer, {}, main_model_related_field='custom_field_id',
                                                            current_model_pk_field='option_id')

        custom_data = {
            "custom_field": custom_field_update[0] if custom_field_update else {},
            "custom_field_options": custom_field_options_update if custom_field_options_update else []
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
    
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a custom field and its related options.
        """
        try:
            instance = self.get_object(pk)
            if not instance:
                return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

            # Delete related CustomFieldOptions
            if not delete_multi_instance(pk, CustomField, CustomFieldOption, main_model_field_name='custom_field_id'):
                return build_response(0, "Error deleting related custom field options", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Delete the main CustomField instance
            instance.delete()

            logger.info(f"CustomField with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)

        except CustomField.DoesNotExist:
            logger.warning(f"CustomField with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting CustomField with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    