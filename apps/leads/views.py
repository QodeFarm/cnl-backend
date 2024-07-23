import logging
from django.http import Http404
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import viewsets, status
from .models import *
from .serializers import *
from config.utils_methods import build_response, delete_multi_instance, generic_data_creation, list_all_objects, create_instance, update_instance, update_multi_instances, validate_input_pk, validate_multiple_data, validate_payload_data, validate_put_method_data
from rest_framework.views import APIView

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

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class LeadAssignmentsView(viewsets.ModelViewSet):
    queryset = LeadAssignments.objects.all()
    serializer_class = LeadAssignmentsSerializer

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
            serializer = LeadsSerializer(queryset, many=True)
            logger.info("lead data retrieved successfully.")
            return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a lead and its related data (items, attachments, and shipments).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the Leads instance
            lead = get_object_or_404(Leads, pk=pk)
            lead_serializer = LeadsSerializer(lead)

            # Retrieve assignment_data
            assignment_data = self.get_related_data(LeadAssignments, LeadAssignmentsSerializer, 'lead_id', pk)
            assignment_data = assignment_data[0] if assignment_data else {}

            # Retrieve assignment_history_data
            assignment_history_data = self.get_related_data(LeadAssignmentHistory, LeadAssignmentHistorySerializer, 'lead_id', pk)
            assignment_history_data = assignment_history_data[0] if assignment_history_data else {}

            # Retrieve interaction_data
            interaction_data = self.get_related_data(LeadInteractions, LeadInteractionsSerializer, 'lead_id', pk)
            interaction_data = interaction_data[0] if interaction_data else {}

            # Customizing the response data
            custom_data = {
                "lead": lead_serializer.data,
                "assignment": assignment_data,
                "assignment_history": assignment_history_data,
                "interaction":interaction_data
                }
            logger.info("lead and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("Sale order with pk %s does not exist.", pk)
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
        Handles the deletion of a lead and its related attachments and shipments.
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

        # Vlidated Leads Data
        lead_data = given_data.pop('lead', None)  # parent_data
        if lead_data:
            lead_error = validate_payload_data(self, lead_data, LeadsSerializer)
            if lead_error:
                errors["lead"] = lead_error

        # Vlidated LeadAssignments Data
        assignment_data = given_data.pop('assignment', None)
        if assignment_data:
            assignment_error = validate_multiple_data(self, assignment_data, LeadAssignmentsSerializer, ['lead_id'])
            if assignment_error:
                errors["assignment"] = assignment_error

        # Vlidated LeadInteractions Data
        interaction_data = given_data.pop('interaction', None)
        if interaction_data:
            interaction_error = validate_multiple_data(self, interaction_data, LeadInteractionsSerializer, ['lead_id'])
            if interaction_error:
                errors["interaction"] = interaction_error

        # Ensure mandatory data is present
        if not lead_data:
            logger.error("Lead data is mandatory but not provided.")
            return build_response(0, "Lead data is mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        if lead_data and interaction_data and not assignment_data: 
            return build_response(0, "without assignment no interaction is possible", [], status.HTTP_400_BAD_REQUEST)

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.
        custom_data = {
            'lead':{},
            'assignment':{},
            'assignment_history':{},
            'interaction':{}
            }

        # Create Leads Data
        new_lead_data = generic_data_creation(self, [lead_data], LeadsSerializer)
        new_lead_data = new_lead_data[0]
        custom_data["lead"] = new_lead_data
        lead_id = new_lead_data.get("lead_id", None)  # Fetch lead_id from mew instance
        logger.info('Leads - created*')

        # Create LeadAssignments Data
        if assignment_data:
            update_fields = {'lead_id': lead_id}
            assignments_data = generic_data_creation(self, [assignment_data], LeadAssignmentsSerializer, update_fields)
            assignments_data = assignments_data[0] if assignments_data else {}
            custom_data["assignment"] = assignments_data
            sales_rep_id = assignment_data.get("sales_rep_id", None)  # Fetch sales_rep_id
            logger.info('LeadAssignments - created*')

            # Create LeadAssignmentHistory Data if LeadAssignments is present
            assignment_history = {}
            update_fields = {'lead_id': lead_id, 'sales_rep_id': sales_rep_id}
            assignments_history = generic_data_creation(self, [assignment_history], LeadAssignmentHistorySerializer, update_fields)
            assignments_history = assignments_history[0] if assignments_history else {}
            custom_data["assignment_history"] = assignments_history
            logger.info('LeadAssignmentHistory - created*')

            # Create LeadInteractions Data if LeadAssignments is present (if no assignment then no interaction)
            if interaction_data:
                update_fields = {'lead_id': lead_id}
                interactions_data = generic_data_creation(self, [interaction_data], LeadInteractionsSerializer, update_fields)
                interactions_data = interactions_data[0] if interactions_data else {}
                custom_data["interaction"] = interactions_data
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

        # Validate LeadAssignments Data
        assignment_data = given_data.pop('assignment', None)
        exclude_fields = ['lead_id']
        if assignment_data:
            assignment_data['lead_id'] = pk
            assignment_error = validate_multiple_data(self, [assignment_data], LeadAssignmentsSerializer, exclude_fields)
            if assignment_error:
                errors["assignment"] = assignment_error

        # Validate LeadAssignmentHistory Data
        assignment_history_data = given_data.pop('assignment_history', None)
        if assignment_history_data:
            assignment_history_data['lead_id'] = pk
            history_error = validate_multiple_data(self, [assignment_history_data], LeadAssignmentHistorySerializer, exclude_fields)
            if history_error:
                errors["assignment_history"] = history_error

        # Validate LeadInteractions Data
        interaction_data = given_data.pop('interaction', None)
        if interaction_data:
            interaction_data['lead_id'] = pk
            interaction = validate_multiple_data(self, [interaction_data], LeadInteractionsSerializer, exclude_fields)
            if interaction:
                errors["interaction"] = interaction

        # Ensure mandatory data is present
        if lead_data and interaction_data and not assignment_data: 
            return build_response(0, "without assignment no interaction is possible", [], status.HTTP_400_BAD_REQUEST)        

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        custom_data = {
            'lead':{},
            'assignment':{},
            'assignment_history':{},
            'interaction':{},
            }

        # update 'Leads'
        if lead_data:
            leaddata = update_multi_instances(self, pk, lead_data, Leads, LeadsSerializer,[], main_model_related_field='lead_id', current_model_pk_field='lead_id')
            custom_data["lead"] = leaddata[0]

        # Update the 'LeadAssignments'
        update_fields = {'lead_id': pk}
        assignmentdata = update_multi_instances(self, pk, assignment_data, LeadAssignments, LeadAssignmentsSerializer, update_fields, main_model_related_field='lead_id', current_model_pk_field='assignment_id')
        if assignmentdata:
            custom_data["assignment"] = assignmentdata[0]

        # create assignment_history_data when 'LeadAssignments' data is added in PUT method
        assignment_history_data_status = False
        if assignment_data:
            if not assignment_history_data:
                # verify if any previous instance is present with current "lead_id", if not present then create new instance in 'LeadAssignmentHistory'
                if not LeadAssignmentHistory.objects.filter(lead_id=pk):
                    assignment_history = {}
                    update_fields = {'lead_id': pk, 'sales_rep_id': assignment_data.get('sales_rep_id')}
                    assignments_history = generic_data_creation(self, [assignment_history], LeadAssignmentHistorySerializer, update_fields)
                    assignments_history = assignments_history[0] if assignments_history else {}
                    custom_data["assignment_history"] = assignments_history
                    assignment_history_data_status = True
                    logger.info('LeadAssignmentHistory - created*')

        # Update the 'LeadAssignmentHistory'
        if assignment_history_data_status == False: # 'False' means it is old instance then update it
            assignmenthistory_data = update_multi_instances(self, pk, assignment_history_data, LeadAssignmentHistory, LeadAssignmentHistorySerializer, update_fields, main_model_related_field='lead_id', current_model_pk_field='history_id')
            if assignmenthistory_data:
                custom_data["assignment_history"] = assignmenthistory_data[0]

        # Update the 'LeadInteractions'
        interactiondata = update_multi_instances(self, pk, interaction_data, LeadInteractions, LeadInteractionsSerializer, update_fields, main_model_related_field='lead_id', current_model_pk_field='interaction_id')
        if interactiondata:
            custom_data["interaction"] = interactiondata[0]

        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

