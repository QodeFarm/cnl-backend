# from itertools import count
import logging
from django.http import Http404
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from apps.leads.filters import LeadsFilter
from config.utils_filter_methods import apply_sorting, filter_by_pagination, filter_response
from .models import *
from .serializers import *
from config.utils_methods import build_response, generic_data_creation, get_object_or_none, list_all_objects, create_instance, update_instance, update_multi_instances, validate_input_pk, validate_multiple_data, validate_payload_data
from rest_framework.views import APIView
from datetime import datetime
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

class LeadStatusesView(viewsets.ModelViewSet):
    queryset = LeadStatuses.objects.all()
    serializer_class = LeadStatusesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class InteractionTypesView(viewsets.ModelViewSet):
    queryset = InteractionTypes.objects.all()
    serializer_class = InteractionTypesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class LeadsView(viewsets.ModelViewSet):
    queryset = Leads.objects.all()
    serializer_class = LeadsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = LeadsFilter
    ordering_fields = []

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class LeadInteractionsView(viewsets.ModelViewSet):
    queryset = LeadInteractions.objects.all()
    serializer_class = LeadInteractionsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class LeadAssignmentHistoryView(viewsets.ModelViewSet):
    queryset = LeadAssignmentHistory.objects.all()
    serializer_class = LeadAssignmentHistorySerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


#------------  API --------------
class LeadsViewSet(APIView):
    """
    API ViewSet for handling Lead creation and related data.
    """

    def get_object(self, pk):
        try:
            return Leads.objects.get(pk=pk)
        except Leads.DoesNotExist:
            logger.warning(f"Leads with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all lead")
            queryset = Leads.objects.all()

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = Leads.objects.count()
                        
            # Apply filters manually
            if request.query_params:
                filterset = LeadsFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs

            serializer = LeadsSerializer(queryset, many=True)
            logger.info("lead data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a lead and its related data (assignment_history, and Interaction).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the Leads instance
            lead = get_object_or_404(Leads, pk=pk)
            lead_serializer = LeadsSerializer(lead)

            # Retrieve assignment_history_data
            assignment_history_data = self.get_related_data(LeadAssignmentHistory, LeadAssignmentHistorySerializer, 'lead_id', pk)
            assignment_history_data = assignment_history_data if assignment_history_data else []

            # Retrieve interaction_data
            interaction_data = self.get_related_data(LeadInteractions, LeadInteractionsSerializer, 'lead_id', pk)
            interaction_data = interaction_data if interaction_data else []

            # Customizing the response data
            custom_data = {
                "lead": lead_serializer.data,
                "assignment_history": assignment_history_data,
                "interaction":interaction_data
                }
            logger.info("lead and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Lead record with pk %s does not exist.", pk)
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
            logger.debug("Retrieved related data for model %s with filter %s=%s.",
                         model.__name__, filter_field, filter_value)
            return serializer.data
        except Exception as e:
            logger.exception("Error retrieving related data for model %s with filter %s=%s: %s",
                             model.__name__, filter_field, filter_value, str(e))
            return []

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a lead and its related assignments and interactions.
        """
        try:
            # Get the Leads instance
            instance = Leads.objects.get(pk=pk)

            # Delete the main Leads instance
            '''
            All related instances will be deleted when parent record is deleted. all child models have foreignkey relation with parent table
            '''
            instance.delete()

            logger.info(f"Leads with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except Leads.DoesNotExist:
            logger.warning(f"Leads with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting Leads with ID {pk}: {str(e)}")
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

        # Validate Leads Data
        lead_data = given_data.pop('lead', None)  # parent_data
        if lead_data:
            lead_error = validate_payload_data(self, lead_data, LeadsSerializer)

            # Get lead_status_id from LeadStatuses model
            lead_status = get_object_or_none(LeadStatuses, status_name='Open') # Default is Open
            if lead_status is not None:
                lead_status_id = lead_status.lead_status_id
                lead_data['lead_status_id'] = lead_status_id # assign default value as 'Open'
            else:
                error_list = []
                if len(lead_error) > 0:
                    lead_error.append({'lead_status_id':["Invalid lead_status_id."]})
                    errors["lead"] = error_list
                else:
                    error_list.append({'lead_status_id':["Invalid lead_status_id."]})
                    errors["lead"] = error_list

            if lead_error:
                errors["lead"] = lead_error

        # Ensure mandatory data is present
        if not lead_data:
            logger.error("Lead data is mandatory but not provided.")
            return build_response(0, "Lead data is mandatory", [], status.HTTP_400_BAD_REQUEST)

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.
        custom_data = {
            'lead':{},
            'assignment_history':[],
            'interaction':[]
            }

        # Create Leads Data
        new_lead_data = generic_data_creation(self, [lead_data], LeadsSerializer)
        new_lead_data = new_lead_data[0]
        custom_data["lead"] = new_lead_data
        lead_id = new_lead_data.get("lead_id", None)  # Fetch lead_id from mew instance
        assignee_id = new_lead_data.get("assignee_id", None)  # Fetch lead_id from mew instance
        logger.info('Leads - created*')

        #create History for Lead with assignemnt date as current and leave the end date as null.
        update_fields = {'lead_id':lead_id, 'assignee_id':assignee_id}
        assignment_history = {}
        assignments_history = generic_data_creation(self, [assignment_history], LeadAssignmentHistorySerializer, update_fields)
        assignments_history = assignments_history if assignments_history else []
        custom_data["assignment_history"] = assignments_history
        logger.info('LeadAssignmentHistory - created*')

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

        # Validate Leads Data
        lead_data = given_data.pop('lead', None)  # parent_data
        if lead_data:
            lead_data['lead_id'] = pk
            lead_error = validate_multiple_data(self, [lead_data], LeadsSerializer, [])
            if lead_error:
                errors["lead"] = lead_error

        # Validate LeadInteractions Data
        interaction_data = given_data.pop('interaction', None)
        if interaction_data:
            interaction = validate_multiple_data(self, interaction_data, LeadInteractionsSerializer, exclude_fields=['lead_id','interaction_type_id'])
            if interaction:
                errors["interaction"] = interaction

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        custom_data = {
            'lead':{},
            'assignment_history':[],
            'interaction':[],
            }
        
        '''
        This "save_assignments_history_with_end_date" function saves the instance in 'LeadAssignmentHistory' model
        by updating the end date.
        '''
        def save_assignments_history_with_end_date(self):
            now = datetime.now()
            end_date = now.strftime('%Y-%m-%d %H:%M:%S')
            history_data_set = LeadAssignmentHistory.objects.filter(lead_id=pk).order_by('created_at').last()
            history_data_set.end_date = end_date # update with end date
            history_data_set.save() # save the record
            logger.info(f'last history_id : {history_data_set}')

        '''
        This "create_new_history" function creates the new instance in 'LeadAssignmentHistory' model
        with required fields to be updated.
        '''
        def create_new_history(self,update_fields):
            assignment_history = {}
            assignments_history = generic_data_creation(self, [assignment_history], LeadAssignmentHistorySerializer, update_fields)
            assignments_history = assignments_history if assignments_history else []
            logger.info('LeadAssignmentHistory - created*')

        if lead_data:
            '''
            This block performs updation of end date in case of 'assignee_id' and 'lead_status_id' is changed.
            (detects changes in 'Leads' payload)
            Adds new record in 'LeadAssignmentHistory' if 'assignee_id' in 'Leads' is changed
            by leaving end date as null.
            Updates old record in 'LeadAssignmentHistory' if 'lead_status_id' in 'Leads' is changed
            by adding end date
            '''
            # Fetch last record in 'Leads' | generally one recrd exists with one 'lead_id' (current Lead pk)
            lead_data_set = Leads.objects.filter(pk=pk).last()  # take the last instance in Lead data
            if lead_data_set is not None:
                previous_lead_status_id = str(lead_data_set.lead_status_id_id)
                current_lead_status_id = lead_data.get('lead_status_id')

                previous_assignee_id = str(lead_data_set.assignee_id_id)
                current_assignee_id = lead_data.get('assignee_id')

                if previous_lead_status_id != current_lead_status_id: # if 'lead_status_id' change is detected
                    logger.info("'lead_status_id' is changed**")
                    save_assignments_history_with_end_date(self)

                if previous_assignee_id != current_assignee_id: # if 'assignee_id' change is detected
                    logger.info("'assignee_id' is changed**")
                    save_assignments_history_with_end_date(self)
                    update_fields = {'lead_id': pk, 'assignee_id': current_assignee_id}
                    create_new_history(self, update_fields)

        # update 'Leads'
        if lead_data:
            leaddata = update_multi_instances(self, pk, lead_data, Leads, LeadsSerializer,[], main_model_related_field='lead_id', current_model_pk_field='lead_id')
            custom_data["lead"] = leaddata[0]

        # Update the 'LeadInteractions'
        update_fields = {'lead_id': pk, 'assignee_id': lead_data.get('assignee_id')}
        interactiondata = update_multi_instances(self, pk, interaction_data, LeadInteractions, LeadInteractionsSerializer, update_fields, main_model_related_field='lead_id', current_model_pk_field='interaction_id')
        if interactiondata:
            custom_data["interaction"] = interactiondata

        # Send the History_data to output response
        history_data = LeadAssignmentHistory.objects.filter(lead_id=pk).order_by('created_at').last()
        if history_data:
            serializer = LeadAssignmentHistorySerializer(history_data)
            custom_data["assignment_history"] = [serializer.data]

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
