from django.http import  Http404
from django.db import transaction
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets,status
from config.utils_methods import list_all_objects, create_instance, update_instance, build_response, validate_input_pk, delete_multi_instance, validate_payload_data, validate_multiple_data, generic_data_creation, update_multi_instances
from apps.tasks.serializers import TasksSerializer,TaskCommentsSerializer,TaskAttachmentsSerializer,TaskHistorySerializer
from apps.tasks.models import Tasks,TaskComments,TaskAttachments,TaskHistory
import logging

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
class TasksViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class TaskCommentsViewSet(viewsets.ModelViewSet):
    queryset = TaskComments.objects.all()
    serializer_class = TaskCommentsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class TaskAttachmentsViewSet(viewsets.ModelViewSet):
    queryset = TaskAttachments.objects.all()
    serializer_class = TaskAttachmentsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class TaskHistoryViewSet(viewsets.ModelViewSet):
    queryset = TaskHistory.objects.all()
    serializer_class = TaskHistorySerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

#------------  API --------------  
class TaskView(APIView):
    """
    API ViewSet for handling Lead creation and related data.
    """

    def get_object(self, pk):
        try:
            return Tasks.objects.get(pk=pk)
        except Tasks.DoesNotExist:
            logger.warning(f"Tasks with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
                
    def get(self, request, *args, **kwargs):
        if 'pk' in kwargs:
           result =  validate_input_pk(self,kwargs['pk'])
           return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            instance = Tasks.objects.all()
        except Tasks.DoesNotExist:
            logger.error("Tasks does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        else:
            serializer = TasksSerializer(instance, many=True)
            logger.info("Tasks data retrieved successfully.")
            return build_response(instance.count(), "Success", serializer.data, status.HTTP_200_OK) 
			
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a task and its related data (taskcomments, taskattachments, and taskhistory).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the Tasks instance
            task = get_object_or_404(Tasks, pk=pk)
            task_serializer = TasksSerializer(task)

            # Retrieve TaskComments data
            task_comments_data = self.get_related_data(TaskComments, TaskCommentsSerializer, 'task_id', pk)

            # Retrieve TaskAttachments data
            task_attachments_data = self.get_related_data(TaskAttachments, TaskAttachmentsSerializer, 'task_id', pk)

            # Retrieve TaskHistory data
            task_history_data = self.get_related_data(TaskHistory, TaskHistorySerializer, 'task_id', pk)
            task_history_data = task_history_data[0] if task_history_data else {}

            # Customizing the response data
            custom_data = {
                "task": task_serializer.data,
                "task_comments": task_comments_data,
				"task_attachments": task_attachments_data,
                "task_history": task_history_data
            }
            logger.info("task and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Task with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving lead with pk %s: %s", pk, str(e))
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
        Handles the deletion of a Tasks and its related TaskComments ,TaskAttachments and TaskHistory

        """
        try:
            # Get the Task instance
            instance = Tasks.objects.get(pk=pk)

            # Delete the main Tasks instance
            instance.delete()

            logger.info(f"Tasks with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except Tasks.DoesNotExist:
            logger.warning(f"Tasks with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting Tasks with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # Handling POST requests for creating
    # To avoid the error this method should be written [error : "detail": "Method \"POST\" not allowed."]
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        # Extracting data from the request
        given_data = request.data

        # ---------------------- D A T A   V A L I D A T I O N ----------------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        errors = {}        

        # Vlidated Tasks Data
        task_data = given_data.pop('task', None)  # parent_data
        if task_data:
            task_error = validate_payload_data(self, task_data, TasksSerializer)
            if task_error:
                errors["task"] = task_error

        # Vlidated TaskComments Data
        task_comments_data = given_data.pop('task_comments', None)
        if task_comments_data:
            task_comments_error = validate_multiple_data(self, task_comments_data, TaskCommentsSerializer, ['task_id'])
            if task_comments_error:
                errors["task_comments"] = task_comments_error

        # Vlidated TaskAttachments Data
        task_attachments_data = given_data.pop('task_attachments', None)
        if task_attachments_data:
            task_attachments_error = validate_multiple_data(self, task_attachments_data, TaskAttachmentsSerializer, ['task_id'])
            if task_attachments_error:
                errors["task_attachments"] = task_attachments_error

        # Vlidated TaskHistory Data
        task_history_data = given_data.pop('task_history', None)
        if task_history_data:
            task_history_error = validate_multiple_data(self, task_history_data, TaskHistorySerializer, ['task_id'])
            if task_history_error:
                errors["task_history"] = task_history_error

        # Ensure mandatory data is present
        if not task_data:
            logger.error("Task data is mandatory but not provided.")
            return build_response(0, "Task data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)
        
        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.

        # Create Tasks Data
        new_task_data = generic_data_creation(self, [task_data], TasksSerializer)
        new_task_data = new_task_data[0]
        task_id = new_task_data.get("task_id", None)  # Fetch task_id from mew instance
        logger.info('Tasks - created*')

        # Create TaskComments Data
        if task_comments_data:
            update_fields = {'task_id': task_id}
            task_comments_data = generic_data_creation(self, task_comments_data, TaskCommentsSerializer, update_fields)
            logger.info('TaskComments - created*')

        # Create TaskAttachments Data
        if task_attachments_data:
            update_fields = {'task_id': task_id}
            task_attachments_data = generic_data_creation(self, task_attachments_data, TaskAttachmentsSerializer, update_fields)
            logger.info('TaskAttachments - created*')

        # Create TaskHistory Data if Tasks is present
        user_id = new_task_data.get("user_id", None) # Fetch user_id from  new_task_data
        status_id = new_task_data.get("status_id", None)# Fetch status_id from  new_task_data
        task_history_data = {}
        update_fields = {'task_id': task_id, 'user_id': user_id, 'status_id': status_id}
        task_history_data = generic_data_creation(self, [task_history_data], TaskHistorySerializer, update_fields)
        logger.info('TaskHistory - created*')#If Task is created then Initial TaskHistory is created

        custom_data = {
            "task": new_task_data,
            "task_comments": task_comments_data,
            "task_attachments": task_attachments_data,
            "task_history":task_history_data[0] if task_history_data else {}
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
        errors = {}

        # Validate Tasks Data
        task_data = given_data.pop('task', None)  # parent_data
        if task_data:
            task_data['task_id'] = pk
            task_error = validate_multiple_data(self, [task_data], TasksSerializer, [])
            if task_error:
                errors["task"] = task_error

        # Validate TaskComments Data
        task_comments_data = given_data.pop('task_comments', None)
        exclude_fields = ['task_id']
        if task_comments_data:
            for data in task_comments_data:
                data['task_id'] = pk
            task_comments_error = validate_multiple_data(self, task_comments_data, TaskCommentsSerializer, exclude_fields)
            if task_comments_error:
                errors["task_comments"] = task_comments_error

        # Validate TaskAttachments Data
        task_attachments_data = given_data.pop('task_attachments', None)
        if task_attachments_data:
            for data in task_attachments_data:
                data['task_id'] = pk
            task_attachments_error = validate_multiple_data(self, task_attachments_data, TaskAttachmentsSerializer, exclude_fields)
            if task_attachments_error:
                errors["task_attachments"] = task_attachments_error

        # Validate TaskHistory Data
        task_history_data = given_data.pop('task_history', None)
        if task_history_data:
            task_history_data['task_id'] = pk
            task_history_error = validate_multiple_data(self, [task_history_data], TaskHistorySerializer, exclude_fields)
            if task_history_error:
                errors["task_history"] = task_history_error

        # Ensure mandatory data is present
        if not task_data:
            logger.error("Task data is mandatory but not provided.")
            return build_response(0, "Task data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)
        
        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        # update Tasks
        if task_data:
            update_fields = [] # No need to update any fields
            taskdata = update_multi_instances(self, pk, task_data, Tasks, TasksSerializer, update_fields,main_model_related_field='task_id', current_model_pk_field='task_id')
            taskdata = taskdata[0] if len(taskdata)==1 else taskdata

        # Update the 'TaskComments'
        update_fields = {'task_id':pk}
        taskcomments_data = update_multi_instances(self, pk, task_comments_data, TaskComments, TaskCommentsSerializer, update_fields, main_model_related_field='task_id', current_model_pk_field='comment_id')

        # Update the 'TaskComments'
        taskattachments_data = update_multi_instances(self, pk, task_attachments_data, TaskAttachments, TaskAttachmentsSerializer, update_fields, main_model_related_field='task_id', current_model_pk_field='attachment_id')

        # Update the 'TaskHistory'
        taskhistory_data = update_multi_instances(self, pk, task_history_data, TaskHistory, TaskHistorySerializer, update_fields, main_model_related_field='task_id', current_model_pk_field='history_id')
        taskhistory_data = taskhistory_data[0] if len(taskhistory_data)==1 else taskhistory_data

        custom_data = {
            "task":taskdata,
            "task_comments":taskcomments_data if taskcomments_data else [],
            "task_attachments":taskattachments_data if taskattachments_data else [],
            "task_history":taskhistory_data if taskhistory_data else {}
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)