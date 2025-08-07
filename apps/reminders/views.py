import logging
from django.shortcuts import render
from rest_framework.views import APIView
from django.http import  Http404
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets,status
from config.utils_filter_methods import filter_response, list_filtered_objects
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter
from .models import NotificationFrequencies, NotificationMethods, ReminderTypes, Reminders, ReminderRecipients, ReminderSettings, ReminderLogs
from .serializers import NotificationFrequenciesSerializer, NotificationMethodsSerializer, ReminderTypesSerializer, RemindersSerializer, ReminderRecipientsSerializer, ReminderSettingsSerializer, ReminderLogsSerializer
from .filters import NotificationFrequenciesFilter, NotificationMethodsFilter, ReminderTypesFilter, RemindersFilter, ReminderRecipientsFilter, ReminderSettingsFilter, ReminderLogsFilter
from config.utils_methods import generic_data_creation, list_all_objects, create_instance, update_instance, soft_delete, build_response, validate_input_pk, update_multi_instances, validate_multiple_data, validate_payload_data , get_related_data, validate_put_method_data

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

# Create your views here.

class NotificationFrequenciesViewSet(viewsets.ModelViewSet):
    queryset = NotificationFrequencies.objects.all().order_by('-created_at')	
    serializer_class = NotificationFrequenciesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = NotificationFrequenciesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, NotificationFrequencies,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
		
class NotificationMethodsViewSet(viewsets.ModelViewSet):
    queryset = NotificationMethods.objects.all().order_by('-created_at')
    serializer_class = NotificationMethodsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = NotificationMethodsFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, NotificationMethods,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
class ReminderTypesViewSet(viewsets.ModelViewSet):
    queryset = ReminderTypes.objects.all().order_by('-created_at')
    serializer_class = ReminderTypesSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ReminderTypesFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ReminderTypes,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
class RemindersViewSet(viewsets.ModelViewSet):
    queryset = Reminders.objects.all().order_by('-created_at')
    serializer_class = RemindersSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = RemindersFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Reminders,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
		
class ReminderRecipientsViewSet(viewsets.ModelViewSet):
    queryset = ReminderRecipients.objects.all().order_by('-created_at')
    serializer_class = ReminderRecipientsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ReminderRecipientsFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
class ReminderSettingsViewSet(viewsets.ModelViewSet):
    queryset = ReminderSettings.objects.all().order_by('-created_at')
    serializer_class = ReminderSettingsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ReminderSettingsFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ReminderSettings,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
		
		
class ReminderLogsViewSet(viewsets.ModelViewSet):
    queryset = ReminderLogs.objects.all().order_by('-created_at')
    serializer_class = ReminderLogsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ReminderLogsFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    

#=================================   Reminders - API   =========================================

class ReminderView(APIView):
    """
    API ViewSet for handling Lead creation and related data.
    """

    def get_object(self, pk):
        try:
            return Reminders.objects.get(pk=pk)
        except Reminders.DoesNotExist:
            logger.warning(f"Reminders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        
    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all lead")
            queryset = Reminders.objects.all().order_by('-created_at')

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = Reminders.objects.count()
                        
            # Apply filters manually
            if request.query_params:
                filterset = RemindersFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs

            serializer = RemindersSerializer(queryset, many=True)
            logger.info("lead data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a reminders and its related data (reminder_recipients and reminder_logs).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the reminders instance
            reminders = get_object_or_404(Reminders, pk=pk)
            reminders_serializer = RemindersSerializer(reminders)

            # Retrieve reminder_recipients data
            reminder_recipients_data = self.get_related_data(ReminderRecipients, ReminderRecipientsSerializer, 'reminder_id', pk)

            # Retrieve reminder_logs data
            reminder_logs_data = self.get_related_data(ReminderLogs, ReminderLogsSerializer, 'reminder_id', pk)
            reminder_logs_data = reminder_logs_data[0] if len(reminder_logs_data)>0 else {}
            # reminder_logs_data = reminder_logs_data if reminder_logs_data else []

            # Customizing the response data
            custom_data = {
                "reminders": reminders_serializer.data,
                "reminder_recipients": reminder_recipients_data,
                "reminder_logs": reminder_logs_data
            }
            logger.info("Reminders and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        
        except Http404:
            logger.error("Reminders with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving Reminders with pk %s: %s", pk, str(e))
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
        Handles the deletion of a reminders and its related reminder_recipients and reminder_logs

        """
        try:
            # Get the Reminders instance
            instance = Reminders.objects.get(pk=pk)

            # Delete the main Reminders instance
            instance.delete()

            logger.info(f"Reminders with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except Reminders.DoesNotExist:
            logger.warning(f"Reminders with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting Reminders with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    @transaction.atomic
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

        errors = {} 
        
        # Vlidated reminders Data
        reminders_data = given_data.pop('reminders', None)  # parent_data
        if reminders_data:
            reminders_error = validate_payload_data(self, reminders_data, RemindersSerializer)
            if reminders_error:
                errors["reminders"] = reminders_error

        # Vlidated reminder_recipients Data
        reminder_recipients_data = given_data.pop('reminder_recipients', None)
        if reminder_recipients_data:
            reminder_recipients_error = validate_multiple_data(self, reminder_recipients_data, ReminderRecipientsSerializer, ['reminder_id'])
            if reminder_recipients_error:
                errors["reminder_recipients"] = reminder_recipients_error

        # # Vlidated reminder_logs Data
        # reminder_logs_data = given_data.pop('reminder_logs', None)
        # if reminder_logs_data:
        #     reminder_logs_error = validate_multiple_data(self, [reminder_logs_data], ReminderLogsSerializer, ['reminder_id'])
        #     if reminder_logs_error:
        #         errors["reminder_logs"] = reminder_logs_error


        # Validated reminder_logs Data
        reminder_logs_data = given_data.pop('reminder_logs', None)

        # If reminder_logs is not provided, set the default log_action to "Created"
        if not reminder_logs_data:
            reminder_logs_data = {
                "log_action": "Created"
            }
        else:
            reminder_logs_error = validate_multiple_data(self, [reminder_logs_data], ReminderLogsSerializer, ['reminder_id'])
            if reminder_logs_error:
                errors["reminder_logs"] = reminder_logs_error

        # Ensure mandatory data is present
        if not reminders_data:
            logger.error("Reminders data is mandatory but not provided.")
            return build_response(0, "Reminders data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        if errors:
            return build_response(0, "ValidationError :", errors, status_code=status.HTTP_400_BAD_REQUEST)
        
        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create reminders Data
        new_reminders_data = generic_data_creation(self, [reminders_data], RemindersSerializer)
        new_reminders_data = new_reminders_data[0]
        reminder_id = new_reminders_data.get("reminder_id", None)  # Fetch reminder_id from mew instance
        logger.info('Reminders - created*')

        # Create reminder_recipients Data
        if reminder_recipients_data:
            update_fields = {'reminder_id': reminder_id}
            reminder_recipients_data = generic_data_creation(self, reminder_recipients_data, ReminderRecipientsSerializer, update_fields)
            logger.info('ReminderRecipients - created*')

        # Create reminder_logs Data
        # if reminder_logs_data:
        #     update_fields = {'reminder_id': reminder_id}
        #     reminder_logs_data = generic_data_creation(self, [reminder_logs_data], ReminderLogsSerializer, update_fields)
        #     logger.info('ReminderLogs - created*')

        # Create reminder_logs Data
        update_fields = {'reminder_id': reminder_id}
        reminder_logs_data = generic_data_creation(self, [reminder_logs_data], ReminderLogsSerializer, update_fields)
        logger.info('ReminderLogs - created*')


        custom_data = {
            "reminders": new_reminders_data,
            "reminder_recipients": reminder_recipients_data,
            "reminder_logs":reminder_logs_data[0] if reminder_logs_data else {}
        }

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):

        # ----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

       # Validate Reminders Data
        reminders_data = given_data.pop('reminders', None)  # parent_data
        if reminders_data:
            reminders_error = validate_payload_data(self, reminders_data, RemindersSerializer)

        # Validated ReminderRecipients Data
        reminder_recipients_data = given_data.pop('reminder_recipients', None)
        if reminder_recipients_data:
            exclude_fields = ['reminder_id']
            reminder_recipients_error = validate_put_method_data(self, reminder_recipients_data, ReminderRecipientsSerializer, exclude_fields, ReminderRecipients, current_model_pk_field='recipient_id')
        else:
            reminder_recipients_error = [] 

        # # Validated ReminderLogs Data
        reminder_logs_data = given_data.pop('reminder_logs', None)
        if reminder_logs_data:
            exclude_fields = ['reminder_id']
            reminder_logs_error = validate_put_method_data(self, [reminder_logs_data], ReminderLogsSerializer, exclude_fields, ReminderLogs, current_model_pk_field='log_id')
        else:
            reminder_logs_error = [] 

        # Ensure mandatory data is present
        if not reminders_data:
            logger.error("Reminders data is mandatory but not provided.")
            return build_response(0, "Reminders data is mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if reminders_error:
            errors["reminders"] = reminders_error
        if reminder_recipients_error:
            errors["reminder_recipients_data"] = reminder_recipients_error
        if reminder_logs_error:
            errors['reminder_logs'] = reminder_logs_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
        
        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        # update PurchaseOrders
        if reminders_data:
            update_fields = {} # No need to update any fields
            remindersdata = update_multi_instances(self, pk, [reminders_data], Reminders, RemindersSerializer, update_fields,main_model_related_field='reminder_id', current_model_pk_field='reminder_id')
            remindersdata = remindersdata[0] if len(remindersdata)==1 else remindersdata

        # Update the 'ReminderRecipients'
        update_fields = {'reminder_id':pk}
        recipients_data = update_multi_instances(self, pk, reminder_recipients_data, ReminderRecipients, ReminderRecipientsSerializer, update_fields, main_model_related_field='reminder_id', current_model_pk_field='recipient_id')

        # Update the 'ReminderLogs'
        logs_data = update_multi_instances(self, pk, reminder_logs_data, ReminderLogs, ReminderLogsSerializer, update_fields, main_model_related_field='reminder_id', current_model_pk_field='log_id')
        logs_data = logs_data[0] if len(logs_data)==1 else logs_data


        custom_data = {
            "reminders": remindersdata,
            "reminder_recipients": recipients_data if recipients_data else [],
            "reminder_logs":logs_data if logs_data else {}            
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)