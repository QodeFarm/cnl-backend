import logging
from .models import *
from .serializers import *
from django.http import Http404
from django.db import transaction
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from config.utils_methods import build_response, generic_data_creation, list_all_objects, create_instance, update_instance, update_multi_instances, validate_input_pk, validate_multiple_data, validate_payload_data , get_related_data, validate_put_method_data

# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

# Create your views here.

class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all()
    serializer_class = BankAccountSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ChartOfAccountsViewSet(viewsets.ModelViewSet):
    queryset = ChartOfAccounts.objects.all()
    serializer_class = ChartOfAccountsSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.all()
    serializer_class = JournalEntrySerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class JournalEntryLinesViewSet(viewsets.ModelViewSet):
    queryset = JournalEntryLines.objects.all()
    serializer_class = JournalEntryLinesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class PaymentTransactionViewSet(viewsets.ModelViewSet):
    queryset = PaymentTransaction.objects.all()
    serializer_class = PaymentTransactionSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class TaxConfigurationViewSet(viewsets.ModelViewSet):
    queryset = TaxConfiguration.objects.all()
    serializer_class = TaxConfigurationSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all()
    serializer_class = BudgetSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ExpenseClaimViewSet(viewsets.ModelViewSet):
    queryset = ExpenseClaim.objects.all()
    serializer_class = ExpenseClaimSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class FinancialReportViewSet(viewsets.ModelViewSet):
    queryset = FinancialReport.objects.all()
    serializer_class = FinancialReportSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)


#--------------------API View-----------------------#
class JournalEntryView(APIView):
    """
    API ViewSet for handling JournalEntry creation and related data.
    """

    def get_object(self, pk):
        try:
            return JournalEntry.objects.get(pk=pk)
        except JournalEntry.DoesNotExist:
            logger.warning(f"JournalEntry with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all JournalEntry")
            queryset = JournalEntry.objects.all()
            serializer = JournalEntrySerializer(queryset, many=True)
            logger.info("JournalEntry data retrieved successfully.")
            return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves a JournalEntry and its related data (JournalEntryLines).
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            # Retrieve the JournalEntry instance
            data = get_object_or_404(JournalEntry, pk=pk)
            journal_serializer = JournalEntrySerializer(data)

            # Retrieve JournalEntryLines instances
            journal_entry_lines_data = get_related_data(JournalEntryLines, JournalEntryLinesSerializer, 'journal_entry_id', pk)
            journal_entry_lines_data = journal_entry_lines_data if journal_entry_lines_data else []

            # Customizing the response data
            custom_data = {
                "journal_entry": journal_serializer.data,
                "journal_entry_lines": journal_entry_lines_data
                }
            logger.info("JournalEntry and related data retrieved successfully.")
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)

        except Http404:
            logger.error("JournalEntry record with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception(
                "An error occurred while retrieving JournalEntry with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the deletion of a JournalEntry and its related data.
        """
        try:
            # Get the JournalEntry instance
            instance = JournalEntry.objects.get(pk=pk)

            # Delete the main JournalEntry instance
            '''
            All related instances will be deleted when parent record is deleted. all child models have foreignkey relation with parent table
            '''
            instance.delete()

            logger.info(f"JournalEntry with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except JournalEntry.DoesNotExist:
            logger.warning(f"JournalEntry with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting JournalEntry with ID {pk}: {str(e)}")
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

        # Validate journal_entry Data
        journal_entry_data = given_data.pop('journal_entry', None)  # parent_data

        # Ensure mandatory data is present
        if not journal_entry_data:
            logger.error("journal entry is mandatory but not provided.")
            return build_response(0, "journal entry is mandatory", [], status.HTTP_400_BAD_REQUEST)
        else:
            journal_entry_error = validate_payload_data(self, journal_entry_data, JournalEntrySerializer)

            if journal_entry_error:
                errors["journal_entry"] = journal_entry_error

        # Validate journal_entry_lines Data
        journal_entry_lines_data = given_data.pop('journal_entry_lines', None)
        if journal_entry_lines_data:
            lines_error = validate_multiple_data(self, journal_entry_lines_data, JournalEntryLinesSerializer,['journal_entry_id'])

            if lines_error:
                errors["journal_entry_lines"] = lines_error

        if errors:
            return build_response(0, "ValidationError :", errors, status.HTTP_400_BAD_REQUEST)

        # ---------------------- D A T A   C R E A T I O N ----------------------------#
        """
        After the data is validated, this validated data is created as new instances.
        """

        # Hence the data is validated , further it can be created.
        custom_data = {
            'journal_entry':{},
            'journal_entry_lines':[]
            }

        # Create JournalEntry Data
        new_journal_entry_data = generic_data_creation(self, [journal_entry_data], JournalEntrySerializer)
        entry_data = new_journal_entry_data[0]
        custom_data["journal_entry"] = entry_data
        logger.info('JournalEntry - created*')

        journal_entry_id = entry_data.get("journal_entry_id", None)  # Fetch journal_entry_id from mew instance

        #create JournalEntryLines
        update_fields = {'journal_entry_id':journal_entry_id}
        lines_data = generic_data_creation(self, journal_entry_lines_data, JournalEntryLinesSerializer, update_fields)
        lines_data = lines_data if lines_data else []
        custom_data["journal_entry_lines"] = lines_data
        logger.info('JournalEntryLines - created*')

        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)
    
    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)
    
    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        #----------------------------------- D A T A  V A L I D A T I O N -----------------------------#
        """
        All the data in request will be validated here. it will handle the following errors:
        - Invalid data types
        - Invalid foreign keys
        - nulls in required fields
        """
        # Get the given data from request
        given_data = request.data

        # Validated JournalEntry Data
        journal_entry_data = given_data.pop('journal_entry', None)
        if journal_entry_data:
            entry_error = validate_payload_data(self, journal_entry_data , JournalEntrySerializer)

        # Validated JournalEntryLines Data
        journal_entry_lines_data = given_data.pop('journal_entry_lines', None)
        if journal_entry_lines_data:
            exclude_fields = ['journal_entry_id']
            lines_error = validate_put_method_data(self, journal_entry_lines_data,JournalEntryLinesSerializer, exclude_fields, JournalEntryLines,current_model_pk_field='journal_entry_line_id')
        else:
            lines_error = [] # Since 'JournalEntryLines' is optional, so making an error is empty list

        # Ensure mandatory data is present
        if not journal_entry_data:
            logger.error("JournalEntry data mandatory but not provided.")
            return build_response(0, "JournalEntry data mandatory but not provided.", [], status.HTTP_400_BAD_REQUEST)
        
        errors = {}
        if entry_error:
            errors["journal_entry"] = entry_error
        if lines_error:
            errors["journal_entry_lines"] = lines_error
        if errors:
            return build_response(0, "ValidationError :",errors, status.HTTP_400_BAD_REQUEST)
            
            # ------------------------------ D A T A   U P D A T I O N -----------------------------------------#
        try:
            # Update the 'JournalEntry'
            if journal_entry_data:
                update_fields = []# No need to update any fields
                journal_data = update_multi_instances(self, pk, [journal_entry_data], JournalEntry, JournalEntrySerializer, update_fields,main_model_related_field='journal_entry_id', current_model_pk_field='journal_entry_id')

            # Update JournalEntryLines Data
            update_fields = {'journal_entry_id':pk}
            lines_data = update_multi_instances(self,pk, journal_entry_lines_data, JournalEntryLines, JournalEntryLinesSerializer, update_fields, main_model_related_field='journal_entry_id', current_model_pk_field='journal_entry_line_id')

            custom_data = [
                {"journal_entry":journal_data[0]},
                {"journal_entry_lines":lines_data if lines_data else []}
            ]

            return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)
        except Exception:
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
#--------------------------------APIView--------------------------
from rest_framework.response import Response
from apps.sales.models import SaleOrder
from apps.purchase.models import PurchaseOrders
from apps.sales.serializers import SaleOrderSerializer
from apps.purchase.serializers import PurchaseOrdersSerializer

class InvoiceListView(APIView):
    def get(self, request, *args, **kwargs):
        order_type = request.query_params.get('order_type')

        if order_type == 'Sale':
            invoices = SaleOrder.objects.all()
            serializer = SaleOrderSerializer(invoices, many=True)
        elif order_type == 'Purchase':
            invoices = PurchaseOrders.objects.all()
            serializer = PurchaseOrdersSerializer(invoices, many=True)
        else:
            return Response({"error": "Invalid order_type"}, status=400)

        return Response(serializer.data, status=200)
