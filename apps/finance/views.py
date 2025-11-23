import datetime
from decimal import Decimal
import logging
from django.forms import IntegerField
from apps.customer.filters import LedgerAccountsFilters
from apps.finance.filters import AgingReportFilter, BalanceSheetReportFilter, BankAccountFilter, BankReconciliationReportFilter, BudgetFilter, CashFlowReportFilter, ChartOfAccountsFilter,  ExpenseClaimFilter, ExpenseItemFilter, FinancialReportFilter, GeneralLedgerReportFilter, JournalEntryFilter, JournalEntryLineFilter, JournalEntryReportFilter, PaymentTransactionFilter, ProfitLossReportFilter, TaxConfigurationFilter, TrialBalanceReportFilter, JournalEntryLinesListFilter
from apps.sales.models import SaleInvoiceOrders
from .models import *
from .serializers import *
from django.http import Http404
from django.db import transaction
from rest_framework import viewsets, status
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from config.utils_methods import build_response, generic_data_creation, list_all_objects, soft_delete, create_instance, update_instance, update_multi_instances, validate_input_pk, validate_multiple_data, validate_payload_data , get_related_data, validate_put_method_data
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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
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
    def post(self, customer_id, ledger_account_id, amount, description, balance_amount, invoice_no):
        '''load_data_in_journal_entry_line_after_payment_transaction. This is used in the apps.sales.view.PaymentTransactionAPIView class.'''
        try:
            # Use serializer to create journal entry line
            print("amount in JournalEntryLinesAPIView", amount)
            entry_data = {
                "customer_id": customer_id,
                "ledger_account_id": ledger_account_id,
                "credit": (amount),
                "description": description,
                "balance" : (balance_amount),
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
            elif LedgerAccounts.objects.filter(pk=input_id).exists():
                queryset = JournalEntryLines.objects.filter(ledger_account_id=input_id).order_by('-created_at')
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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
      
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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)

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
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)
    
 
# class ExpenseCategoryViewSet(viewsets.ModelViewSet):
#     queryset = ExpenseCategory.objects.all().order_by('-created_at')
#     serializer_class = ExpenseCategorySerializer
#     filter_backends = [DjangoFilterBackend,OrderingFilter]
#     filterset_class = ExpenseCategoryFilter
#     ordering_fields = ['created_at']
    

#     def list(self, request, *args, **kwargs):
#         print("Inside list method")
#         return list_filtered_objects(self, request, ExpenseCategory,*args, **kwargs)

#     def create(self, request, *args, **kwargs):
#         return create_instance(self, request, *args, **kwargs)

#     def update(self, request, *args, **kwargs):
#         return update_instance(self, request, *args, **kwargs)
    
#     def destroy(self, request, *args, **kwargs):
#         instance = self.get_object()
#         return soft_delete(instance)

class ExpenseItemViewSet(viewsets.ModelViewSet):
    queryset = ExpenseItem.objects.all().order_by('-created_at')
    serializer_class = ExpenseItemSerializer
    filter_backends = [DjangoFilterBackend,OrderingFilter]
    filterset_class = ExpenseItemFilter
    ordering_fields = ['created_at']
   

    def list(self, request, *args, **kwargs):
        print("Inside list method")
        return list_filtered_objects(self, request,*args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        return soft_delete(instance)


#--------------------Custom API View for ExpenseItem-----------------------#
class ExpenseItemView(APIView):
    """
    Custom API View for handling ExpenseItem creation, update, and related data.
    Following the same pattern as JournalEntryView.
    """

    def get_object(self, pk):
        try:
            return ExpenseItem.objects.get(pk=pk)
        except ExpenseItem.DoesNotExist:
            logger.warning(f"ExpenseItem with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

    def get(self, request, *args, **kwargs):
        if "pk" in kwargs:
            result = validate_input_pk(self, kwargs['pk'])
            return result if result else self.retrieve(self, request, *args, **kwargs)
        try:
            logger.info("Retrieving all ExpenseItem")
            queryset = ExpenseItem.objects.all().order_by('-created_at')

            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 10))
            total_count = ExpenseItem.objects.count()

            # Apply filters manually
            if request.query_params:
                filterset = ExpenseItemFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs

            serializer = ExpenseItemSerializer(queryset, many=True)
            logger.info("ExpenseItem data retrieved successfully.")
            return filter_response(queryset.count(), "Success", serializer.data, page, limit, total_count, status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"An unexpected error occurred: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves an ExpenseItem by ID.
        """
        try:
            pk = kwargs.get('pk')
            if not pk:
                logger.error("Primary key not provided in request.")
                return build_response(0, "Primary key not provided", [], status.HTTP_400_BAD_REQUEST)

            data = get_object_or_404(ExpenseItem, pk=pk)
            serializer = ExpenseItemSerializer(data)

            logger.info("ExpenseItem retrieved successfully.")
            return build_response(1, "Success", serializer.data, status.HTTP_200_OK)

        except Http404:
            logger.error("ExpenseItem record with pk %s does not exist.", pk)
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.exception("An error occurred while retrieving ExpenseItem with pk %s: %s", pk, str(e))
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Handles the soft deletion of an ExpenseItem.
        """
        try:
            instance = ExpenseItem.objects.get(pk=pk)
            instance.is_deleted = True
            instance.save()

            logger.info(f"ExpenseItem with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except ExpenseItem.DoesNotExist:
            logger.warning(f"ExpenseItem with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting ExpenseItem with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted ExpenseItem record.
        """
        try:
            instance = ExpenseItem.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"ExpenseItem with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save()

            logger.info(f"ExpenseItem with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except ExpenseItem.DoesNotExist:
            logger.warning(f"ExpenseItem with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring ExpenseItem with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Creates a new ExpenseItem and automatically posts to Journal Entry.
        """
        from decimal import Decimal
        from apps.customer.models import LedgerAccounts

        # Validate and create expense item
        serializer = ExpenseItemSerializer(data=request.data)
        if not serializer.is_valid():
            return build_response(0, "Validation Error", serializer.errors, status.HTTP_400_BAD_REQUEST)

        expense = serializer.save()
        logger.info(f'ExpenseItem created: {expense.expense_item_id}')

        # Validation
        if not expense.ledger_account_id:
            return build_response(
                0,
                "Expense is not linked to a Ledger Account. Please set 'ledger_account_id' for this expense.",
                [],
                status.HTTP_400_BAD_REQUEST
            )

        # Create JournalEntry
        journal_entry = JournalEntry.objects.create(
            entry_date=expense.expense_date,
            reference=expense.reference_number,
            description=expense.description,
            voucher_type='ExpenseVoucher'
        )
        logger.info(f'JournalEntry created for expense: {journal_entry.voucher_no}')

        # Debit Expense Ledger Account
        voucher_no = expense.reference_number if expense.reference_number else ''
        JournalEntryLines.objects.create(
            journal_entry_id=journal_entry,
            ledger_account_id=expense.ledger_account_id,
            debit=expense.amount,
            credit=0,
            description=f"Expense: {expense.description}",
            vendor_id=expense.vendor_id,
            customer_id=None,
            voucher_no=voucher_no,
            balance=0
        )

        # Credit Bank/Cash Account
        if expense.bank_account_id:
            bank_ledger_account = LedgerAccounts.objects.filter(bank_account_id=expense.bank_account_id).first()
            if bank_ledger_account:
                JournalEntryLines.objects.create(
                    journal_entry_id=journal_entry,
                    ledger_account_id=bank_ledger_account,
                    debit=0,
                    credit=expense.amount,
                    description=f"Paid from {expense.bank_account_id.account_name}",
                    vendor_id=expense.vendor_id,
                    customer_id=None,
                    voucher_no=voucher_no,
                    balance=0
                )

        # Recalculate balances for affected ledger accounts
        affected_accounts = [expense.ledger_account_id]
        if expense.bank_account_id:
            bank_ledger = LedgerAccounts.objects.filter(bank_account_id=expense.bank_account_id).first()
            if bank_ledger:
                affected_accounts.append(bank_ledger)

        for ledger_account in affected_accounts:
            if ledger_account:
                ledger_lines = JournalEntryLines.objects.filter(
                    ledger_account_id=ledger_account,
                    is_deleted=False
                ).order_by('journal_entry_id__entry_date', 'created_at', 'journal_entry_line_id')

                running_balance = Decimal('0.00')
                for line in ledger_lines:
                    debit = Decimal(str(line.debit)) if line.debit else Decimal('0.00')
                    credit = Decimal(str(line.credit)) if line.credit else Decimal('0.00')
                    running_balance = running_balance + debit - credit

                    if line.balance != running_balance:
                        JournalEntryLines.objects.filter(
                            journal_entry_line_id=line.journal_entry_line_id
                        ).update(balance=running_balance)

        logger.info('Running balances recalculated for affected ledger accounts')

        return build_response(1, "Record created successfully", serializer.data, status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        """
        Updates an existing ExpenseItem and its related Journal Entry.
        """
        from decimal import Decimal
        from apps.customer.models import LedgerAccounts

        try:
            expense = ExpenseItem.objects.get(pk=pk)
        except ExpenseItem.DoesNotExist:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)

        serializer = ExpenseItemSerializer(expense, data=request.data, partial=True)
        if not serializer.is_valid():
            return build_response(0, "Validation Error", serializer.errors, status.HTTP_400_BAD_REQUEST)

        expense = serializer.save()
        logger.info(f'ExpenseItem updated: {expense.expense_item_id}')

        # Update JournalEntry
        journal_entry = JournalEntry.objects.filter(reference=expense.reference_number).first()
        if journal_entry:
            journal_entry.entry_date = expense.expense_date
            journal_entry.description = expense.description
            journal_entry.save()

            # Track affected ledger accounts for balance recalculation
            affected_accounts = set()

            # Update debit line (expense ledger account)
            debit_line = JournalEntryLines.objects.filter(
                journal_entry_id=journal_entry,
                debit__gt=0
            ).first()
            if debit_line:
                # Track old account if changed
                if debit_line.ledger_account_id != expense.ledger_account_id:
                    affected_accounts.add(debit_line.ledger_account_id)

                debit_line.debit = expense.amount
                debit_line.description = f"Expense: {expense.description}"
                debit_line.vendor_id = expense.vendor_id
                debit_line.voucher_no = expense.reference_number or ''
                debit_line.ledger_account_id = expense.ledger_account_id
                debit_line.save()
                affected_accounts.add(expense.ledger_account_id)

            # Update or create credit line (bank/cash account)
            if expense.bank_account_id:
                bank_ledger_account = LedgerAccounts.objects.filter(bank_account_id=expense.bank_account_id).first()
                credit_line = JournalEntryLines.objects.filter(
                    journal_entry_id=journal_entry,
                    credit__gt=0
                ).first()
                if credit_line:
                    # Track old account if changed
                    if credit_line.ledger_account_id != bank_ledger_account:
                        affected_accounts.add(credit_line.ledger_account_id)

                    credit_line.credit = expense.amount
                    credit_line.description = f"Paid from {expense.bank_account_id.account_name}"
                    credit_line.vendor_id = expense.vendor_id
                    credit_line.voucher_no = expense.reference_number or ''
                    credit_line.ledger_account_id = bank_ledger_account
                    credit_line.save()
                    if bank_ledger_account:
                        affected_accounts.add(bank_ledger_account)

            # Recalculate balances for all affected ledger accounts
            for ledger_account in affected_accounts:
                if ledger_account:
                    ledger_lines = JournalEntryLines.objects.filter(
                        ledger_account_id=ledger_account,
                        is_deleted=False
                    ).order_by('journal_entry_id__entry_date', 'created_at', 'journal_entry_line_id')

                    running_balance = Decimal('0.00')
                    for line in ledger_lines:
                        debit = Decimal(str(line.debit)) if line.debit else Decimal('0.00')
                        credit = Decimal(str(line.credit)) if line.credit else Decimal('0.00')
                        running_balance = running_balance + debit - credit

                        if line.balance != running_balance:
                            JournalEntryLines.objects.filter(
                                journal_entry_line_id=line.journal_entry_line_id
                            ).update(balance=running_balance)

            logger.info('Running balances recalculated for affected ledger accounts')

        return build_response(1, "Record updated successfully", serializer.data, status.HTTP_200_OK)

    
    	
class GeneralAccountsListAPIView(APIView):
    def get(self, request):
        accounts = LedgerAccounts.objects.filter(type__in=['Bank', 'Cash'], is_deleted=False)
        serializer = GeneralAccountSerializer(accounts, many=True)
        return Response({
            "count": len(serializer.data),
            "msg": "SUCCESS",
            "data": serializer.data
        }, status=200)

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
    def cash_book(self, request):
        """Generates the Cash Book Report."""
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        
        cash_accounts = LedgerAccounts.objects.filter(type='Cash', is_deleted=False)
        # Show newest first for better UX
        queryset = JournalEntryLines.objects.filter(
            ledger_account_id__in=cash_accounts
        ).order_by('-journal_entry_id__entry_date', '-created_at', '-journal_entry_line_id')
        
        total_count = queryset.count()
        
        # Apply filters if query parameters are present
        if request.query_params:
            filterset = JournalEntryLineFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
        
        serializer = GeneralLedgerReportSerializer(queryset, many=True)
        return filter_response(queryset.count(), "Cash Book Report", serializer.data, page, limit, total_count, status.HTTP_200_OK)

    @action(detail=False, methods=['get'])
    def bank_book(self, request):
        """Generates the Bank Book Report."""
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        
        bank_accounts = LedgerAccounts.objects.filter(type='Bank', is_deleted=False)
        # Show newest first for better UX
        queryset = JournalEntryLines.objects.filter(
            ledger_account_id__in=bank_accounts
        ).order_by('-journal_entry_id__entry_date', '-created_at', '-journal_entry_line_id')
        
        total_count = queryset.count()
        
        # Apply filters if query parameters are present
        if request.query_params:
            filterset = JournalEntryLineFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
        
        serializer = GeneralLedgerReportSerializer(queryset, many=True)
        return filter_response(queryset.count(), "Bank Book Report", serializer.data, page, limit, total_count, status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'])
    def general_ledger(self, request):
        """Generates the General Ledger Report."""
        logger.info("Generating General Ledger Report")
        from decimal import Decimal
        
        # Base queryset - Filter first
        base_queryset = JournalEntryLines.objects.select_related('ledger_account_id', 'journal_entry_id') \
                                            .filter(is_deleted=False)

        # Apply filters if query parameters are present
        if request.query_params:
            filterset = JournalEntryLineFilter(request.GET, queryset=base_queryset)
            if filterset.is_valid():
                base_queryset = filterset.qs
        
        # Get the filtered ledger accounts BEFORE pagination
        ledger_account_ids = list(base_queryset.values_list('ledger_account_id', flat=True).distinct())
        
        # Recalculate balances for filtered accounts to ensure correctness
        for ledger_account_id in ledger_account_ids:
            if ledger_account_id:
                # Get all lines for this account in chronological order
                account_lines = JournalEntryLines.objects.filter(
                    ledger_account_id=ledger_account_id,
                    is_deleted=False
                ).order_by('journal_entry_id__entry_date', 'created_at', 'journal_entry_line_id')
                
                running_balance = Decimal('0.00')
                for line in account_lines:
                    debit = Decimal(str(line.debit)) if line.debit else Decimal('0.00')
                    credit = Decimal(str(line.credit)) if line.credit else Decimal('0.00')
                    running_balance = running_balance + debit - credit
                    
                    if line.balance != running_balance:
                        JournalEntryLines.objects.filter(
                            journal_entry_line_id=line.journal_entry_line_id
                        ).update(balance=running_balance)
        
        # Now order for display (newest first)
        final_queryset = base_queryset.order_by('ledger_account_id__name', '-journal_entry_id__entry_date', '-created_at', '-journal_entry_line_id')

        # Serialize
        serializer = GeneralLedgerReportSerializer(final_queryset, many=True)
        return Response({"count": final_queryset.count(),"msg": "General Ledger Report","data": serializer.data}, status=200)


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

        queryset = JournalEntry.objects.all().order_by('-created_at')
        total_count = queryset.count()

        # Apply filters if query parameters are present
        if request.query_params:
            filterset = JournalEntryReportFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        serializer = JournalEntryReportSerializer(queryset, many=True)
        return filter_response(queryset.count(),"Success",serializer.data,page,limit,total_count,status.HTTP_200_OK)
    
    @action(detail=False, methods=['post'])
    def recalculate_all_balances(self, request):
        """Recalculates all journal entry line balances for all ledger accounts"""
        from decimal import Decimal
        from apps.customer.models import LedgerAccounts
        
        try:
            ledger_accounts = LedgerAccounts.objects.filter(is_deleted=False)
            total_accounts = ledger_accounts.count()
            total_lines_updated = 0
            
            for ledger_account in ledger_accounts:
                # Get all lines for this ledger account in chronological order
                ledger_lines = JournalEntryLines.objects.filter(
                    ledger_account_id=ledger_account,
                    is_deleted=False
                ).order_by('journal_entry_id__entry_date', 'created_at', 'journal_entry_line_id')
                
                if not ledger_lines.exists():
                    continue
                
                running_balance = Decimal('0.00')
                for line in ledger_lines:
                    debit = Decimal(str(line.debit)) if line.debit else Decimal('0.00')
                    credit = Decimal(str(line.credit)) if line.credit else Decimal('0.00')
                    running_balance = running_balance + debit - credit
                    
                    if line.balance != running_balance:
                        JournalEntryLines.objects.filter(
                            journal_entry_line_id=line.journal_entry_line_id
                        ).update(balance=running_balance)
                        total_lines_updated += 1
            
            return Response({
                "count": 1,
                "msg": f"Successfully recalculated balances for {total_accounts} accounts. Updated {total_lines_updated} lines.",
                "data": {
                    "accounts_processed": total_accounts,
                    "lines_updated": total_lines_updated
                }
            }, status=200)
            
        except Exception as e:
            logger.error(f"Error recalculating balances: {str(e)}")
            return Response({
                "count": 0,
                "msg": f"Error recalculating balances: {str(e)}",
                "data": []
            }, status=500)

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
            instance.is_deleted=True
            instance.save()

            logger.info(f"JournalEntry with ID {pk} deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)
        except JournalEntry.DoesNotExist:
            logger.warning(f"JournalEntry with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error deleting JournalEntry with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    @transaction.atomic
    def patch(self, request, pk, *args, **kwargs):
        """
        Restores a soft-deleted JournalEntry record (is_deleted=True → is_deleted=False).
        """
        try:
            instance = JournalEntry.objects.get(pk=pk)

            if not instance.is_deleted:
                logger.info(f"JournalEntry with ID {pk} is already active.")
                return build_response(0, "Record is already active", [], status.HTTP_400_BAD_REQUEST)

            instance.is_deleted = False
            instance.save()

            logger.info(f"JournalEntry with ID {pk} restored successfully.")
            return build_response(1, "Record restored successfully", [], status.HTTP_200_OK)

        except JournalEntry.DoesNotExist:
            logger.warning(f"JournalEntry with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error restoring JournalEntry with ID {pk}: {str(e)}")
            return build_response(0, "Record restoration failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
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

        # Recalculate balances for all affected ledger accounts
        # This ensures correct running balances when multiple lines are created simultaneously
        from decimal import Decimal
        from apps.customer.models import LedgerAccounts
        
        affected_ledger_account_ids = set()
        for line in lines_data:
            ledger_account_id = line.get('ledger_account_id')
            if ledger_account_id:
                affected_ledger_account_ids.add(ledger_account_id)
        
        # Recalculate running balances for each affected ledger account
        for ledger_account_id in affected_ledger_account_ids:
            try:
                # Get the LedgerAccount object
                ledger_account = LedgerAccounts.objects.get(ledger_account_id=ledger_account_id)
                
                # Get all lines for this ledger account in chronological order
                # Order by entry_date first, then created_at, then line_id for consistent ordering
                ledger_lines = JournalEntryLines.objects.filter(
                    ledger_account_id=ledger_account,
                    is_deleted=False
                ).order_by('journal_entry_id__entry_date', 'created_at', 'journal_entry_line_id')
                
                running_balance = Decimal('0.00')
                for line in ledger_lines:
                    debit = Decimal(str(line.debit)) if line.debit else Decimal('0.00')
                    credit = Decimal(str(line.credit)) if line.credit else Decimal('0.00')
                    running_balance = running_balance + debit - credit
                    
                    # Only update if balance changed
                    if line.balance != running_balance:
                        line.balance = running_balance
                        JournalEntryLines.objects.filter(
                            journal_entry_line_id=line.journal_entry_line_id
                        ).update(balance=running_balance)
                
                logger.info(f'Recalculated balances for ledger account: {ledger_account.name}')
            except LedgerAccounts.DoesNotExist:
                logger.warning(f'LedgerAccount {ledger_account_id} not found')
                continue
        
        logger.info('Running balances recalculated for affected ledger accounts')

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
            journal_entry_data.pop('voucher_no', None)  # ✅ Remove voucher_no before validation
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
    
    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Soft deletes a journal entry by setting is_deleted=True.
        """
        try:
            instance = Journal.objects.get(pk=pk)
            instance.is_deleted = True
            instance.save()
            logger.info(f"Journal with ID {pk} soft deleted successfully.")
            return build_response(1, "Record deleted successfully", [], status.HTTP_204_NO_CONTENT)

        except Journal.DoesNotExist:
            logger.warning(f"Journal with ID {pk} does not exist.")
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error soft deleting Journal with ID {pk}: {str(e)}")
            return build_response(0, "Record deletion failed due to an error", [], status.HTTP_500_INTERNAL_SERVER_ERROR)



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

