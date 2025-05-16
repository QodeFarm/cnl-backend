import datetime
from decimal import Decimal
import logging
from django.forms import IntegerField
from apps.finance.filters import AgingReportFilter, BalanceSheetReportFilter, BankAccountFilter, BankReconciliationReportFilter, BudgetFilter, CashFlowReportFilter, ChartOfAccountsFilter, ExpenseClaimFilter, FinancialReportFilter, GeneralLedgerReportFilter, JournalEntryFilter, JournalEntryLineFilter, JournalEntryReportFilter, PaymentTransactionFilter, ProfitLossReportFilter, TaxConfigurationFilter, TrialBalanceReportFilter, JournalEntryLinesListFilter
from apps.sales.models import SaleInvoiceOrders
from .models import *
from .serializers import *
from django.http import Http404
from django.db import transaction
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from config.utils_methods import build_response, generic_data_creation, list_all_objects, create_instance, update_instance, update_multi_instances, validate_input_pk, validate_multiple_data, validate_payload_data , get_related_data, validate_put_method_data
from config.utils_filter_methods import filter_response, list_filtered_objects
from django_filters.rest_framework import DjangoFilterBackend 
from rest_framework.filters import OrderingFilter
from rest_framework.response import Response
from .models import Journal
from .serializers import JournalSerializer
from uuid import uuid4
from rest_framework.decorators import action
from django.db.models import Sum, F, Value, DecimalField, ExpressionWrapper, When,Case,DurationField,IntegerField,Q
from django.db.models.functions import Coalesce,Cast
from datetime import date
# Set up basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Create a logger object
logger = logging.getLogger(__name__)

# Create your views here.

class BankAccountViewSet(viewsets.ModelViewSet):
    queryset = BankAccount.objects.all().order_by('-created_at')
    serializer_class = BankAccountSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = BankAccountFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, BankAccount,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class ChartOfAccountsViewSet(viewsets.ModelViewSet):
    queryset = ChartOfAccounts.objects.all().order_by('-created_at')
    serializer_class = ChartOfAccountsSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ChartOfAccountsFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ChartOfAccounts,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class JournalEntryViewSet(viewsets.ModelViewSet):
    queryset = JournalEntry.objects.all().order_by('-created_at')
    serializer_class = JournalEntrySerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = JournalEntryFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class JournalEntryLinesViewSet(viewsets.ModelViewSet):
    queryset = JournalEntryLines.objects.all().order_by('-created_at')
    serializer_class = JournalEntryLinesSerializer

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
class JournalEntryLinesAPIView(APIView):
    def post(self, customer_id, account_id, amount, description, balance_amount, invoice_no):
        '''load_data_in_journal_entry_line_after_payment_transaction. This is used in the apps.sales.view.PaymentTransactionAPIView class.'''
        try:
            # Use serializer to create journal entry line
            entry_data = {
                "customer_id": customer_id,
                "account_id": account_id,
                "credit": int(amount),
                "description": description,
                "balance" : int(balance_amount),
                "voucher_no" : invoice_no
            }
            serializer = JournalEntryLinesSerializer(data=entry_data)
            if serializer.is_valid():
                serializer.save() 
            else:
                raise ValueError(f"serializer validation failed, {serializer.errors}")
        
        except(ValueError, TypeError) as e:
            return build_response(1, f"Invalid Data provided For Journal Entry Lines.", str(e), status.HTTP_406_NOT_ACCEPTABLE)
        
        return build_response(1, "Data Loaded In Journal Entry Lines.", [], status.HTTP_201_CREATED)
    
    def get(self, request, input_id):  
            # Try to determine if this UUID is for a customer
            if Customer.objects.filter(pk=input_id).exists():
                queryset = JournalEntryLines.objects.filter(customer_id=input_id).order_by('-created_at')
            elif Vendor.objects.filter(pk=input_id).exists():
                queryset = JournalEntryLines.objects.filter(vendor_id=input_id).order_by('-created_at')
            else:
                return build_response(0, "Please provide either customer_id or vendor_id.", [], status.HTTP_400_BAD_REQUEST)
            
            # Get pagination parameters
            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10))
            total_count = queryset.count()
            
            # Apply filters if query parameters are present
            if request.query_params:
                filterset = JournalEntryLinesListFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
                    logger.debug(f"Applied filters. Filtered queryset count: {queryset.count()}")

            # Serialize the data
            serializer = JournalEntryLinesSerializer(queryset, many=True)
            
            # Return response using filter_response helper
            return filter_response( count=queryset.count(), message="Journal Entry Lines data", data=serializer.data,page=page,limit=limit,total_count=total_count,status_code=status.HTTP_200_OK)
        
class PaymentTransactionViewSet(viewsets.ModelViewSet):
    queryset = PaymentTransaction.objects.all().order_by('-created_at')
    serializer_class = PaymentTransactionSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = PaymentTransactionFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, PaymentTransaction,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
      
class TaxConfigurationViewSet(viewsets.ModelViewSet):
    queryset = TaxConfiguration.objects.all().order_by('-created_at')
    serializer_class = TaxConfigurationSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = TaxConfigurationFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, TaxConfiguration,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class BudgetViewSet(viewsets.ModelViewSet):
    queryset = Budget.objects.all().order_by('-created_at')
    serializer_class = BudgetSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = BudgetFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, Budget,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class ExpenseClaimViewSet(viewsets.ModelViewSet):
    queryset = ExpenseClaim.objects.all().order_by('-created_at')
    serializer_class = ExpenseClaimSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ExpenseClaimFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, ExpenseClaim,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class FinancialReportViewSet(viewsets.ModelViewSet):
    queryset = FinancialReport.objects.all().order_by('-created_at')
    serializer_class = FinancialReportSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = FinancialReportFilter
    ordering_fields = ['created_at']

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, FinancialReport,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def get_pagination_params(self, request):
        """Extracts pagination parameters from the request."""
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        return page, limit

    @action(detail=False, methods=['get'])
    def general_ledger(self, request):
        """Generates the General Ledger Report with all transactions."""
        logger.info("Generating General Ledger Report")

        # Get pagination parameters
        page, limit = self.get_pagination_params(request)

        # Fetch all journal entry lines, ordered by entry date
        queryset = JournalEntryLines.objects.select_related('journal_entry_id', 'account_id').order_by('-journal_entry_id__entry_date')

        # Apply filters if query parameters are present
        if request.query_params:
            filterset = GeneralLedgerReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        # Get total count of journal entry lines (before pagination)
        total_count = JournalEntryLines.objects.count()
        # Serialize the data
        serializer = GeneralLedgerReportSerializer(queryset, many=True)

        # Return the response using filter_response
        return filter_response(len(queryset),  "General Ledger Report Generated",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def trial_balance(self, request):
        """Generates the Trial Balance Report summarizing account balances."""
        logger.info("Generating Trial Balance Report")
        page, limit = self.get_pagination_params(request)

        # Annotate each ChartOfAccounts instance with aggregated debit, credit and calculate balance.
        queryset = ChartOfAccounts.objects.annotate(
            total_debit=Coalesce(
                Sum('journal_entry_lines__debit'),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
            total_credit=Coalesce(
                Sum('journal_entry_lines__credit'),
                Value(0, output_field=DecimalField(max_digits=15, decimal_places=2))
            )
        ).annotate(
            balance=ExpressionWrapper(
                F('total_debit') - F('total_credit'),
                output_field=DecimalField(max_digits=15, decimal_places=2)
            )
        ).order_by('account_code')
        
        # Apply filters if query parameters are present
        if request.query_params:
            filterset = TrialBalanceReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
                
        total_count = queryset.count()
        serializer = TrialBalanceReportSerializer(queryset, many=True)
        # Get pagination parameters if needed (assuming you have a helper)
        
        return filter_response(total_count,"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)    

    @action(detail=False, methods=['get'])
    def profit_and_loss(self, request):
        """Generates the Profit & Loss Statement."""
        logger.info("Generating Profit & Loss Report")
        page, limit = self.get_pagination_params(request)
        
        # Step 1: Create a queryset
        queryset = ChartOfAccounts.objects.all()
        # Step 2: Apply filters
        filterset = ProfitLossReportFilter(request.GET, queryset=queryset)
        if filterset.is_valid():
            queryset = filterset.qs
            
         # Aggregate revenue for accounts with type 'Revenue'
        revenue_agg = ChartOfAccounts.objects.filter(account_type='Revenue').aggregate(
            total_credit=Coalesce(
                Sum('journal_entry_lines__credit'),
                Value(Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
            total_debit=Coalesce(
                Sum('journal_entry_lines__debit'),
                Value(Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2))
            )
        )
        total_revenue = revenue_agg['total_credit'] - revenue_agg['total_debit']

        # Aggregate expense for accounts with type 'Expense'
        expense_agg = ChartOfAccounts.objects.filter(account_type='Expense').aggregate(
            total_debit=Coalesce(
                Sum('journal_entry_lines__debit'),
                Value(Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2))
            ),
            total_credit=Coalesce(
                Sum('journal_entry_lines__credit'),
                Value(Decimal('0.00'), output_field=DecimalField(max_digits=15, decimal_places=2))
            )
        )
        total_expense = expense_agg['total_debit'] - expense_agg['total_credit']

        # Calculate net profit (or loss)
        net_profit = total_revenue - total_expense
        # Wrap the result in a list so that it matches the UI's expected format (list of objects)
        report_data = [{
            'total_revenue': total_revenue,
            'total_expense': total_expense,
            'net_profit': net_profit
        }]
        
        # Instantiate the serializer with the instance (report_data) and many=True
        serializer = ProfitLossReportSerializer(report_data, many=True)
        # Return using the same response structure as your other reports
        return filter_response( count=len(report_data),  message="Profit & Loss Report Generated",data=serializer.data,page=page,limit=limit,total_count=len(report_data),status_code=status.HTTP_200_OK)
        
    @action(detail=False, methods=['get'])
    def balance_sheet(self, request):
        """Generates the Balance Sheet Report."""
        logger.info("Generating Balance Sheet Report")
        page, limit = self.get_pagination_params(request)

         # Filter for Asset, Liability, and Equity accounts and aggregate debit/credit sums
        queryset = ChartOfAccounts.objects.filter(
            account_type__in=['Asset', 'Liability', 'Equity']
        ).annotate(
            total_debit=Coalesce(
                Sum('journal_entry_lines__debit', output_field=DecimalField(max_digits=18, decimal_places=2)),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))
            ),
            total_credit=Coalesce(
                Sum('journal_entry_lines__credit', output_field=DecimalField(max_digits=18, decimal_places=2)),
                Value(0, output_field=DecimalField(max_digits=18, decimal_places=2))
            )
        ).annotate(
            balance=ExpressionWrapper(
                F('total_debit') - F('total_credit'),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            )
        ).order_by('account_code')
        if request.query_params:
            filterset = BalanceSheetReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = queryset.count()
        serializer = BalanceSheetAccountSerializer(queryset, many=True)

        # Use your helper function to format the response with pagination info
        return filter_response(count=total_count,message="Balance Sheet Report Generated",data=serializer.data,page=page,limit=limit,total_count=total_count,status_code=status.HTTP_200_OK )

    @action(detail=False, methods=['get'])
    def cash_flow(self, request):
        """Generates the Cash Flow Statement."""
        logger.info("Generating Cash Flow Statement")
        page, limit = self.get_pagination_params(request)

        queryset = ChartOfAccounts.objects.filter(
            account_type__in=['Asset', 'Expense', 'Revenue']
        ).annotate(
            total_debit=Coalesce(
                Sum('journal_entry_lines__debit'),
                Value(Decimal('0.00'), output_field=DecimalField(max_digits=18, decimal_places=2))
            ),
            total_credit=Coalesce(
                Sum('journal_entry_lines__credit'),
                Value(Decimal('0.00'), output_field=DecimalField(max_digits=18, decimal_places=2))
            )
        ).annotate(
            cash_inflow=Case(
                When(account_type='Revenue', then=F('total_credit')),
                When(account_type='Asset', then=F('total_credit')),
                default=Value(Decimal('0.00')),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            ),
            cash_outflow=Case(
                When(account_type='Expense', then=F('total_debit')),
                When(account_type='Asset', then=F('total_debit')),
                default=Value(Decimal('0.00')),
                output_field=DecimalField(max_digits=18, decimal_places=2)
            )
        ).order_by('account_code')
        
        if request.query_params:
            filterset = CashFlowReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = queryset.count()
        serializer = CashFlowStatementSerializer(queryset, many=True)

        return filter_response(total_count,"Cash Flow Statement Generated",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def aging_report(self, request):
        """Generates the Aging Report for pending payments."""
        logger.info("Generating Aging Report")
        page, limit = self.get_pagination_params(request)

        today_date = date.today()  # Define today_date before using it
    
        queryset = PaymentTransaction.objects.filter(
            payment_status='Pending'
        ).annotate(
            due_days=Cast(
                ExpressionWrapper(
                    Value(today_date) - F('payment_date'),
                    output_field=DurationField()
                ),
                output_field=IntegerField()
            ),
            pending_amount=Coalesce(Sum('amount'), Value(0, output_field=DecimalField()))
        ).order_by('due_days')
        
        if request.query_params:
            filterset = AgingReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        total_count = queryset.count()
        serializer = AgingReportSerializer(queryset, many=True)

        return filter_response(total_count,"Aging Report Generated",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def bank_reconciliation(self, request):
        """Generates the Bank Reconciliation Report."""
        logger.info("Generating Bank Reconciliation Report")
        page, limit = self.get_pagination_params(request)

        queryset = BankAccount.objects.all().annotate(
        total_debit=Coalesce(
            Sum('linked_accounts__journal_entry_lines__debit'),
            Value(0),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        ),
        total_credit=Coalesce(
            Sum('linked_accounts__journal_entry_lines__credit'),
            Value(0),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    ).annotate(
        ledger_balance=ExpressionWrapper(
            F('total_debit') - F('total_credit'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    ).annotate(
        difference=ExpressionWrapper(
            F('balance') - F('ledger_balance'),
            output_field=DecimalField(max_digits=15, decimal_places=2)
        )
    ).order_by('bank_name')
    
        if request.query_params:
                filterset = BankReconciliationReportFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs

        total_count = queryset.count()
        serializer = BankReconciliationReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def journal_entry_report(self, request):
        """Generates the Journal Entry Report."""
        logger.info("Generating Journal Entry Report")
        page, limit = self.get_pagination_params(request)

        # Fetch all journal entries with their lines
        queryset = JournalEntry.objects.prefetch_related('entry_lines').order_by('-entry_date')
        total_count = queryset.count()
        
        if request.query_params:
            filterset = JournalEntryReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
        # Process data for report
        report_data = []
        for entry in queryset:
            entry_data = {
                'entry_date': entry.entry_date,
                'reference': entry.reference,
                'description': entry.description,
                'lines': []
            }
            for line in entry.entry_lines.all():
                entry_data['lines'].append({
                    'account': line.account_id.account_name if line.account_id else "N/A",
                    'debit': float(line.debit),
                    'credit': float(line.credit),
                    'description': line.description
                })
            report_data.append(entry_data)
        return filter_response(len(report_data), "Journal Entry Report Generated", report_data, page, limit, total_count, status.HTTP_200_OK)


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
            queryset = JournalEntry.objects.all().order_by('-created_at')

            page = int(request.query_params.get('page', 1))  # Default to page 1 if not provided
            limit = int(request.query_params.get('limit', 10)) 
            total_count = JournalEntry.objects.count()

            # Apply filters manually
            if request.query_params:
                filterset = JournalEntryFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs 

            serializer = JournalEntrySerializer(queryset, many=True)
            logger.info("JournalEntry data retrieved successfully.")
            # return build_response(queryset.count(), "Success", serializer.data, status.HTTP_200_OK)
            return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)

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


#FOR LEDGERS
class JournalListCreateAPIView(APIView):
    """
    List all journal entries, or create a new journal entry.
    """
    def get(self, request):
        journals = Journal.objects.all()
        serializer = JournalSerializer(journals, many=True)
        return build_response(len(serializer.data), "Records Retrieved successfully", serializer.data, status.HTTP_200_OK)

    def post(self, request):
        # Generate a new UUID for journal_id
        journal_id = str(uuid4())
        data = request.data.copy()
        data['journal_id'] = journal_id

        serializer = JournalSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return build_response(1, "Records updated successfully", serializer.data, status.HTTP_201_CREATED)
        return build_response(1, "Records Not Created", serializer.errors, status.HTTP_400_BAD_REQUEST) 


class JournalRetrieveUpdateDeleteAPIView(APIView):
    """
    Retrieve, update or delete a journal entry by journal_id.
    """
    def get_object(self, journal_id):
        try:
            return Journal.objects.get(journal_id=journal_id)
        except Journal.DoesNotExist:
            return None

    def get(self, request, journal_id):
        journal = self.get_object(journal_id)
        if journal is None:
            return build_response(0, "Record Not found.", {}, status.HTTP_404_NOT_FOUND) 
        
        serializer = JournalSerializer(journal)
        return build_response(len(serializer.data), "Records Retrieved successfully", serializer.data, status.HTTP_200_OK)

    def put(self, request, journal_id):
        journal = self.get_object(journal_id)
        if journal is None:
            return build_response(0, "Record Not found.", {}, status.HTTP_404_NOT_FOUND) 

        serializer = JournalSerializer(journal, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return build_response(len(serializer.data), "Records updated successfully", serializer.data, status.HTTP_200_OK)
        return build_response(len(serializer.data), "Records Not updated", serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, journal_id):
        try:
            # Get the Journal Id instance
            instance = Journal.objects.get(pk=journal_id)
            instance.delete()

            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except Journal.DoesNotExist:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)


class JournalDetailListCreateAPIView(APIView):
    """
    List all journal details, or create a new journal detail entry.
    """
    def get(self, request):
        journal_details = JournalDetail.objects.all()
        serializer = JournalDetailSerializer(journal_details, many=True)
        return build_response(len(serializer.data), "Records Retrieved successfully", serializer.data, status.HTTP_200_OK)

    def post(self, request):
        # Generate a new UUID for journal_detail_id
        journal_detail_id = str(uuid4())
        data = request.data.copy()
        data['journal_detail_id'] = journal_detail_id

        serializer = JournalDetailSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return build_response(1, "Records updated successfully", serializer.data, status.HTTP_201_CREATED)
        return build_response(1, "Records Not Created", serializer.errors, status.HTTP_400_BAD_REQUEST) 


class JournalDetailRetrieveUpdateDeleteAPIView(APIView):
    """
    Retrieve, update or delete a journal detail entry by journal_detail_id.
    """
    def get_object(self, journal_detail_id):
        try:
            return JournalDetail.objects.get(journal_detail_id=journal_detail_id)
        except JournalDetail.DoesNotExist:
            return None

    def get(self, request, journal_detail_id):
        journal_detail = self.get_object(journal_detail_id)
        if journal_detail is None:
            return build_response(0, "Record Not found.", {}, status.HTTP_404_NOT_FOUND)
        
        serializer = JournalDetailSerializer(journal_detail)
        return build_response(len(serializer.data), "Records Retrieved successfully", serializer.data, status.HTTP_200_OK)

    def put(self, request, journal_detail_id):
        journal_detail = self.get_object(journal_detail_id)
        if journal_detail is None:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = JournalDetailSerializer(journal_detail, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return build_response(len(serializer.data), "Records updated successfully", serializer.data, status.HTTP_200_OK)
        return build_response(len(serializer.data), "Records Not updated", serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def delete(self, request, journal_detail_id):
        journal_detail = self.get_object(journal_detail_id)
        if journal_detail is None:
            return build_response(0, "Record Not found.", "", status.HTTP_404_NOT_FOUND)
        
        journal_detail.delete()
        return build_response(0, "Records Deleted successfully", "", status.HTTP_204_NO_CONTENT)

