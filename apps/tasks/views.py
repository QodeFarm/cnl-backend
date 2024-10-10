from django.http import  Http404
from django.db import transaction
from django.shortcuts import render
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework import viewsets,status
from apps.tasks.filters import TasksFilter
from config.utils_filter_methods import filter_response
from config.utils_methods import list_all_objects, create_instance, update_instance, build_response, validate_input_pk, validate_payload_data, get_object_or_none, validate_multiple_data, generic_data_creation, update_multi_instances
from apps.tasks.serializers import TasksSerializer,TaskCommentsSerializer,TaskAttachmentsSerializer,TaskHistorySerializer
from apps.tasks.models import Tasks,TaskComments,TaskAttachments,TaskHistory
import logging
from apps.masters.models import Statuses
from apps.masters.serializers import ModStatusesSerializer
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Get an instance of a logger
logger = logging.getLogger(__name__)

# Create your views here.
class TasksViewSet(viewsets.ModelViewSet):
    queryset = Tasks.objects.all()
    serializer_class = TasksSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = TasksFilter
    ordering_fields = []

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

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = Tasks.objects.count()

            # Apply filters manually
            if request.query_params:
                queryset = Tasks.objects.all()
                filterset = TasksFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
                    serializer = TasksSerializer(queryset, many=True)
                    # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
                    return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

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
            task_history_data = task_history_data if task_history_data else []

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

        # Validated Tasks Data
        task_data = given_data.pop('task', None)  # parent_data
        # Ensure mandatory data is present
        if not task_data:
            logger.error("Task data is mandatory but not provided.")
            return build_response(0, "Task data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        # Check if either user_id or group_id is provided
        user_id = task_data.get("user_id", None)
        group_id = task_data.get("group_id", None)

        if not user_id and not group_id:
            return build_response(0, "Either user_id or group_id must be provided", [], status.HTTP_400_BAD_REQUEST)

        if user_id and group_id:
            return build_response(0, "Both user_id and group_id cannot be provided at the same time", [], status.HTTP_400_BAD_REQUEST)
        
        # Set default task status to 'Open'
        task_status = get_object_or_none(Statuses, status_name='Open')  # Assuming the default status is 'Open'
        if task_status is not None:
            task_data['status_id'] = task_status.status_id
        else:
            errors["task"] = {"status_id": ["Invalid status_id."]}

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

        if errors:
            return build_response(0, "ValidationError :", errors, status_code=status.HTTP_400_BAD_REQUEST)
        
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

        # Create TaskHistory Data if Task is present
        status_id = new_task_data.get("status_id", None)  # Fetch status_id from new_task_data
        task_history_data = None

        if user_id:
            # Task assigned to a user
            update_fields = {'task_id': task_id, 'user_id': user_id, 'status_id': status_id}
            task_history_data = generic_data_creation(self, [{}], TaskHistorySerializer, update_fields)
        elif group_id:
            # Task assigned to a group 
            update_fields = {'task_id': task_id, 'group_id': group_id, 'status_id': status_id}
            task_history_data = generic_data_creation(self, [{}], TaskHistorySerializer, update_fields)

        logger.info('TaskHistory - created*')  # If Task is created, then initial TaskHistory is created


        custom_data = {
            "task": new_task_data,
            "task_comments": task_comments_data,
            "task_attachments": task_attachments_data,
            "task_history":task_history_data[0] if task_history_data else []
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

            # Ensure that either 'user_id' or 'group_id' is provided but not both
            if task_data.get('user_id') and task_data.get('group_id'):
                errors['task'] = "A task can be assigned either to a user or a group, not both."
            elif not task_data.get('user_id') and not task_data.get('group_id'):
                errors['task'] = "A task must be assigned to either a user or a group."

            # Validate task data
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
            for data in task_history_data:
                data['task_id'] = pk
            exclude_fields = ['task_id', 'user_id', 'group_id', 'status_id']
            task_history_error = validate_multiple_data(self, task_history_data, TaskHistorySerializer, exclude_fields)
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

            def create_new_history(self):
                update_fields = {'task_id': pk, 'status_id': task_data.get('status_id')}
                
                # Assign `user_id` or `group_id` based on what's provided
                if task_data.get('user_id'):
                    update_fields['user_id'] = task_data.get('user_id')
                elif task_data.get('group_id'):
                    update_fields['group_id'] = task_data.get('group_id')

                task_history = generic_data_creation(self, [{}], TaskHistorySerializer, update_fields)
                task_history = task_history if task_history else []
                logger.info("'task_history' is created**")
                return task_history

            # Fetch last record in 'Task' | generally one record exists with one 'task_id'
            data_set = Tasks.objects.filter(task_id=pk).order_by('created_at').last()
            if data_set is not None:
                previous_user_id = str(data_set.user_id_id) 
                previous_group_id = str(data_set.group_id_id) 
                current_user_id = task_data.get('user_id')
                current_group_id = task_data.get('group_id')

                logger.info(f"Previous user ID: {previous_user_id}, Current user ID: {current_user_id}")
                logger.info(f"Previous group ID: {previous_group_id}, Current group ID: {current_group_id}")

                # Check if 'user_id' or 'group_id' changes
                if previous_user_id != str(current_user_id) or (previous_group_id and previous_group_id != str(current_group_id)):
                    logger.info("'user_id' or 'group_id' is changed**")
                    task_history_data = create_new_history(self)

                # Check if 'status_id' change is detected
                previous_status_id = str(data_set.status_id_id)
                current_status_id = task_data.get('status_id')
                if previous_status_id != current_status_id:
                    logger.info("'status_id' is changed**")
                    task_history_data = create_new_history(self)


            update_fields = [] # No need to update any fields
            taskdata = update_multi_instances(self, pk, task_data, Tasks, TasksSerializer, update_fields,main_model_related_field='task_id', current_model_pk_field='task_id')
            taskdata = taskdata[0] if len(taskdata)==1 else taskdata

            # # Update the 'Task'
            # update_fields = []  # No need to update any fields
            # # logger.info(f"Updating task with ID: {pk}, Data: {task_data}")
            # taskdata = update_multi_instances(self, pk, task_data, Tasks, TasksSerializer, update_fields, main_model_related_field='task_id', current_model_pk_field='task_id')

            # # Ensure taskdata is valid
            # if not taskdata:
            #     logger.error(f"Failed to update task with ID: {pk}.")
            #     return build_response(0, "Failed to update task", {}, status.HTTP_400_BAD_REQUEST)

            # taskdata = taskdata[0] if len(taskdata) == 1 else taskdata

        # Update the 'TaskComments'
        update_fields = {'task_id':pk}
        taskcomments_data = update_multi_instances(self, pk, task_comments_data or [], TaskComments, TaskCommentsSerializer, update_fields, main_model_related_field='task_id', current_model_pk_field='comment_id')

        # Update the 'Taskattachments'
        taskattachments_data = update_multi_instances(self, pk, task_attachments_data or [],  TaskAttachments, TaskAttachmentsSerializer, update_fields, main_model_related_field='task_id', current_model_pk_field='attachment_id')

        custom_data = {
            "task":taskdata,
            "task_comments":taskcomments_data if taskcomments_data else [],
            "task_attachments":taskattachments_data if taskattachments_data else [],
            "task_history":task_history_data if task_history_data else []
        }

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)