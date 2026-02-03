import datetime
from decimal import Decimal
import logging
from django.forms import IntegerField
from requests import request
from apps.auditlogs.utils import log_user_action
from apps.customer.filters import LedgerAccountsFilters
from apps.customer.models import CustomerAddresses
from apps.finance.filters import AgingReportFilter, BalanceSheetReportFilter, BankAccountFilter, BankReconciliationReportFilter, BudgetFilter, CashFlowReportFilter, ChartOfAccountsFilter,  ExpenseClaimFilter, ExpenseItemFilter, FinancialReportFilter, GeneralLedgerReportFilter, JournalEntryFilter, JournalEntryLineFilter, JournalEntryReportFilter, PaymentTransactionFilter, ProfitLossReportFilter, TaxConfigurationFilter, TrialBalanceReportFilter, JournalEntryLinesListFilter, JournalVoucherFilter, JournalVoucherLineFilter, JournalBookReportFilter
from apps.sales.models import SaleInvoiceItems, SaleInvoiceOrders
from apps.vendor.models import VendorAddress
from config.utils_db_router import set_db
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
    
    #log actions
    log_actions = True
    log_module_name = "Bank Accounts"
    log_pk_field = "bank_account_id"
    log_display_field = "bank_name"

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
    
    #log actions
    log_actions = True
    log_module_name = "Journal Entry"
    log_pk_field = "journal_entry_id"
    log_display_field = "voucher_no"

    def list(self, request, *args, **kwargs):
        return list_all_objects(self, request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

class JournalEntryLinesViewSet(viewsets.ModelViewSet):
    queryset = JournalEntryLines.objects.all().order_by('-created_at')
    serializer_class = JournalEntryLinesSerializer
    
    #log actions
    log_actions = True
    log_module_name = "Journal Entry Lines"
    log_pk_field = "journal_entry_line_id"
    log_display_field = "description"

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
                
                # log_user_action(
                #     set_db('default'),
                #     request.user,
                #     "CREATE",
                #     "Journal Entry Lines",
                #     journal_entry_line_id,
                #     f"{description} - Custom Fields record created by {request.user.username}"
                # )
            else:
                raise ValueError(f"serializer validation failed, {serializer.errors}")
        
        except(ValueError, TypeError) as e:
            return build_response(1, f"Invalid Data provided For Journal Entry Lines.", str(e), status.HTTP_406_NOT_ACCEPTABLE)
        
        return build_response(1, "Data Loaded In Journal Entry Lines.", [], status.HTTP_201_CREATED)
    
    # def get(self, request, input_id):

    #     # ADD THIS UUID CHECK (NEW – SMALL & SAFE)
    #     is_uuid = True
    #     try:
    #         uuid.UUID(str(input_id))
    #     except ValueError:
    #         is_uuid = False

    #     # EXISTING FLOW (UUID BASED – UNCHANGED)
    #     if is_uuid and Customer.objects.filter(pk=input_id).exists():
    #         queryset = JournalEntryLines.objects.filter(customer_id=input_id).order_by('-created_at')

    #     elif is_uuid and Vendor.objects.filter(pk=input_id).exists():
    #         queryset = JournalEntryLines.objects.filter(vendor_id=input_id).order_by('-created_at')

    #     elif is_uuid and LedgerAccounts.objects.filter(pk=input_id).exists():
    #         queryset = JournalEntryLines.objects.filter(ledger_account_id=input_id).order_by('-created_at')

    #     # 🔵 CITY FLOW (ONLY WHEN input_id IS NOT UUID)
    #     else:
    #         city_id = request.query_params.get('city')

    #         if not city_id:
    #             return build_response(
    #                 0,
    #                 "City is required",
    #                 [],
    #                 status.HTTP_400_BAD_REQUEST
    #             )

    #         if input_id == 'customer_id':
    #             queryset = JournalEntryLines.objects.filter(
    #                 customer_id__in=CustomerAddresses.objects.filter(
    #                     city_id=city_id
    #                 ).values_list('customer_id', flat=True)
    #             ).order_by('-created_at')

    #         elif input_id == 'vendor_id':
    #             queryset = JournalEntryLines.objects.filter(
    #                 vendor_id__in=VendorAddress.objects.filter(
    #                     city_id=city_id
    #                 ).values_list('vendor_id', flat=True)
    #             ).order_by('-created_at')

    #         else:
    #             return build_response(
    #                 0,
    #                 "Invalid account identifier",
    #                 [],
    #                 status.HTTP_400_BAD_REQUEST
    #             )

    #     # ⬇️ REST OF YOUR CODE (UNCHANGED)
    #     page = int(request.query_params.get('page', 1))
    #     limit = int(request.query_params.get('limit', 10))
    #     total_count = queryset.count()

    #     if request.query_params:
    #         filterset = JournalEntryLinesListFilter(request.GET, queryset=queryset, request=request)
    #         if filterset.is_valid():
    #             queryset = filterset.qs

    #     serializer = JournalEntryLinesSerializer(queryset, many=True)

    #     return filter_response(
    #         count=queryset.count(),
    #         message="Journal Entry Lines data",
    #         data=serializer.data,
    #         page=page,
    #         limit=limit,
    #         total_count=total_count,
    #         status_code=status.HTTP_200_OK
    #     )
    
    def get(self, request, input_id):

        # ---------------------------
        # STEP 1: UUID CHECK
        # ---------------------------
        is_uuid = True
        try:
            uuid.UUID(str(input_id))
        except ValueError:
            is_uuid = False

        # ---------------------------
        # STEP 2: BASE QUERYSET
        # ---------------------------
        if is_uuid and Customer.objects.filter(pk=input_id).exists():
            queryset = JournalEntryLines.objects.filter(
                customer_id=input_id,
                is_deleted=False
            ).order_by('-created_at')

        elif is_uuid and Vendor.objects.filter(pk=input_id).exists():
            queryset = JournalEntryLines.objects.filter(
                vendor_id=input_id,
                is_deleted=False
            ).order_by('-created_at')

        elif is_uuid and LedgerAccounts.objects.filter(pk=input_id).exists():
            queryset = JournalEntryLines.objects.filter(
                ledger_account_id=input_id,
                is_deleted=False
            ).order_by('-created_at')

        else:
            # ---------------------------
            # CITY BASED FLOW
            # ---------------------------
            city_id = request.query_params.get('city')

            if not city_id:
                return build_response(
                    0,
                    "City is required",
                    [],
                    status.HTTP_400_BAD_REQUEST
                )

            if input_id == 'customer_id':
                queryset = JournalEntryLines.objects.filter(
                    customer_id__in=CustomerAddresses.objects.filter(
                        city_id=city_id
                    ).values_list('customer_id', flat=True),
                    is_deleted=False
                ).order_by('-created_at')

            elif input_id == 'vendor_id':
                queryset = JournalEntryLines.objects.filter(
                    vendor_id__in=VendorAddress.objects.filter(
                        city_id=city_id
                    ).values_list('vendor_id', flat=True),
                    is_deleted=False
                ).order_by('-created_at')

            else:
                return build_response(
                    0,
                    "Invalid account identifier",
                    [],
                    status.HTTP_400_BAD_REQUEST
                )

        # ---------------------------
        # STEP 3: APPLY FILTERS (WITHOUT PAGINATION)
        # ---------------------------
        filter_params = request.GET.copy()
        filter_params.pop('page', None)
        filter_params.pop('limit', None)

        filterset = JournalEntryLinesListFilter(
            filter_params,
            queryset=queryset,
            request=request
        )

        filtered_queryset = filterset.qs if filterset.is_valid() else queryset

        # ---------------------------
        # STEP 4: TOTAL COUNT (FULL FILTERED COUNT)
        # ---------------------------
        total_count = filtered_queryset.count()

        # ---------------------------
        # STEP 5: PAGINATION (ALWAYS APPLIED)
        # ---------------------------
        page = max(int(request.query_params.get('page', 1)), 1)
        limit = max(int(request.query_params.get('limit', 10)), 1)


        start = (page - 1) * limit
        end = start + limit

        paginated_queryset = filtered_queryset[start:end]

        # ---------------------------
        # STEP 6: SERIALIZATION
        # ---------------------------
        serializer = JournalEntryLinesSerializer(paginated_queryset, many=True)
        data = serializer.data
        
        # Collect invoice numbers from journal entries
        invoice_nos = [
            row.get("voucher_no")
            for row in data
            if row.get("voucher_no") and "Goods sold to" in (row.get("description") or "")
            and "\n1)" not in (row.get("description") or "")
        ]

        # Fetch related invoices in ONE query
        invoice_map = {
            inv.invoice_no: inv
            for inv in SaleInvoiceOrders.objects.filter(invoice_no__in=invoice_nos)
        }

        # Fetch all items in ONE query
        items_map = {}
        invoice_ids = [inv.sale_invoice_id for inv in invoice_map.values()]

        for item in SaleInvoiceItems.objects.filter(sale_invoice_id__in=invoice_ids):
            items_map.setdefault(item.sale_invoice_id, []).append(item)

        # Inject product lines
        for row in data:
            voucher_no = row.get("voucher_no")
            description = row.get("description") or ""

            if (
                voucher_no in invoice_map
                and "\n1)" not in description   # avoid duplicates
            ):
                invoice = invoice_map[voucher_no]
                items = items_map.get(invoice.sale_invoice_id, [])

                product_lines = [
                    f"{idx}) {item.print_name} – Qty: {item.quantity} @ {item.rate}"
                    for idx, item in enumerate(items, start=1)
                ]

                if product_lines:
                    row["description"] = (
                        f"Goods sold to {invoice.customer_id.name}\n"
                        + "\n".join(product_lines)
                    )

        # ---------------------------
        # STEP 7: RESPONSE
        # ---------------------------
        return filter_response(
            count=paginated_queryset.count(),   # page-wise count
            message="Journal Entry Lines data",
            data=serializer.data,
            page=page,
            limit=limit,
            total_count=total_count,             # full count
            status_code=status.HTTP_200_OK
        )





    # def get(self, request, input_id):

    #     # ✅ NEW: check whether input_id is UUID
    #     is_uuid = True
    #     try:
    #         uuid.UUID(str(input_id))
    #     except ValueError:
    #         is_uuid = False

    #     # 🟢 EXISTING FLOW (UUID BASED – NO CHANGE)
    #     if is_uuid and Customer.objects.filter(pk=input_id).exists():
    #         queryset = JournalEntryLines.objects.filter(customer_id=input_id).order_by('-created_at')

    #     elif is_uuid and Vendor.objects.filter(pk=input_id).exists():
    #         queryset = JournalEntryLines.objects.filter(vendor_id=input_id).order_by('-created_at')

    #     elif is_uuid and LedgerAccounts.objects.filter(pk=input_id).exists():
    #         queryset = JournalEntryLines.objects.filter(ledger_account_id=input_id).order_by('-created_at')

    #     # 🔵 NEW FLOW (CITY BASED – ADDED ONLY)
    #     elif not is_uuid:
    

    #     # ⬇️ REST OF YOUR CODE (UNCHANGED)
    #     page = int(request.query_params.get('page', 1))
    #     limit = int(request.query_params.get('limit', 10))
    #     total_count = queryset.count()

    #     if request.query_params:
    #         filterset = JournalEntryLinesListFilter(request.GET, queryset=queryset)
    #         if filterset.is_valid():
    #             queryset = filterset.qs

    #     serializer = JournalEntryLinesSerializer(queryset, many=True)

    #     return filter_response(
    #         count=queryset.count(),
    #         message="Journal Entry Lines data",
    #         data=serializer.data,
    #         page=page,
    #         limit=limit,
    #         total_count=total_count,
    #         status_code=status.HTTP_200_OK
    #     )


        
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
    
    #log actions
    log_actions = True
    log_module_name = "Tax Configuration"
    log_pk_field = "tax_id"
    log_display_field = "tax_name"

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
    
    #log actions
    log_actions = True
    log_module_name = "Budget"
    log_pk_field = "budget_id"
    log_display_field = "fiscal_year"

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
    
    #log actions
    log_actions = True
    log_module_name = "Expense Claim"
    log_pk_field = "expense_claim_id"
    log_display_field = "expense_claim_id"

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
    
    #log actions
    log_actions = True
    log_module_name = "Expense Item"
    log_pk_field = "expense_item_id"
    log_display_field = "expense_item_id"
   

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
        
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))
        
        # Base queryset with ordering applied first
        queryset = JournalEntryLines.objects.select_related('ledger_account_id', 'journal_entry_id') \
                                            .filter(is_deleted=False) \
                                            .order_by('ledger_account_id__name', '-journal_entry_id__entry_date', '-created_at', '-journal_entry_line_id')
        
        total_count = queryset.count()
        
        # Get all unique ledger account IDs from the unfiltered queryset for balance recalculation
        all_ledger_account_ids = list(set(queryset.values_list('ledger_account_id', flat=True)))
        
        # Recalculate balances for all accounts to ensure correctness
        for ledger_account_id in all_ledger_account_ids:
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
        
        # Apply filters if query parameters are present
        if request.query_params:
            filterset = JournalEntryLineFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs

        # Serialize
        serializer = GeneralLedgerReportSerializer(queryset, many=True)
        return filter_response(queryset.count(), "General Ledger Report", serializer.data, page, limit, total_count, status.HTTP_200_OK)


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


# ======================================
# JOURNAL VOUCHER VIEWS
# ======================================
"""
Journal Voucher API Views
--------------------------
Real-time Use Cases:

1. INTER-ACCOUNT ADJUSTMENTS (Most Common)
   - Person A owes Person B, but Person C pays on behalf of A
   - Dr: Person A Account | Cr: Person C Account
   
2. EMPLOYEE EXPENSE ADJUSTMENTS
   - Employee A's expense paid by Employee B
   - Dr: Employee A | Cr: Employee B
   
3. BRANCH/HEAD OFFICE ADJUSTMENTS
   - Branch vendor bill paid by Head Office
   - Dr: Branch Account | Cr: Head Office Account
   
4. CUSTOMER TO CUSTOMER ADJUSTMENTS
   - Customer A advance adjusts Customer B invoice
   - Dr: Customer A | Cr: Customer B
   
5. CONTRA ENTRIES (Cash to Bank)
   - Cash deposited to bank
   - Dr: Bank Account | Cr: Cash Account
   
6. DEPRECIATION ENTRIES
   - Monthly/yearly depreciation
   - Dr: Depreciation Expense | Cr: Accumulated Depreciation
   
7. OPENING BALANCE ENTRIES
   - New financial year opening balances
   
8. PROVISION ENTRIES
   - Bad debt provision, expense provisions
   
Key Rule: Total Debit = Total Credit (Always balanced)
"""


class JournalVoucherView(APIView):
    """
    API View for handling Journal Voucher CRUD operations.
    Follows MaterialIssueView / SaleOrderViewSet pattern.
    
    Supports:
    - GET: List all vouchers or retrieve single voucher with lines & attachments
    - POST: Create voucher with lines and attachments
    - PUT: Update voucher with lines and attachments
    - DELETE: Soft delete voucher
    """
    
    # Log actions for audit trail
    log_actions = True
    log_module_name = "Journal Voucher"
    log_pk_field = "journal_voucher_id"
    log_display_field = "voucher_no"

    def get_object(self, pk):
        """Get single JournalVoucher object or None"""
        try:
            return JournalVoucher.objects.get(pk=pk)
        except JournalVoucher.DoesNotExist:
            return None

    def get(self, request, *args, **kwargs):
        """
        GET Handler:
        - With pk: Returns single voucher with lines and attachments
        - Without pk: Returns paginated list of vouchers
        """
        pk = kwargs.get('pk')
        if pk:
            result = validate_input_pk(self, pk)
            if result:
                return result
            return self.retrieve(request, pk)
        
        # List all vouchers with pagination
        page = int(request.query_params.get("page", 1))
        limit = int(request.query_params.get("limit", 10))

        queryset = JournalVoucher.objects.filter(is_deleted=False).order_by('-created_at')
        
        # Apply filters
        if request.query_params:
            filterset = JournalVoucherFilter(request.GET, queryset=queryset)
            if filterset.is_valid():
                queryset = filterset.qs
        
        serializer = JournalVoucherSerializer(queryset, many=True)
        return filter_response(queryset.count(), "Success", serializer.data, page, limit, queryset.count(), status.HTTP_200_OK)

    def retrieve(self, request, pk):
        """
        Retrieve single voucher with related lines and attachments.
        Returns structured response like MaterialIssue.
        """
        try:
            journal_voucher = get_object_or_404(JournalVoucher, pk=pk)
            serializer = JournalVoucherSerializer(journal_voucher)
            
            # Get related voucher lines and attachments
            lines = get_related_data(JournalVoucherLine, JournalVoucherLineSerializer, 'journal_voucher_id', pk)
            attachments = get_related_data(JournalVoucherAttachment, JournalVoucherAttachmentSerializer, 'journal_voucher_id', pk)
            
            custom_data = {
                "journal_voucher": serializer.data,
                "voucher_lines": lines if lines else [],
                "attachments": attachments if attachments else [],
            }
            return build_response(1, "Success", custom_data, status.HTTP_200_OK)
        except Http404:
            return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error retrieving Journal Voucher: {str(e)}")
            return build_response(0, "An error occurred", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        """POST Handler - Create new Journal Voucher"""
        return self.create(request, *args, **kwargs)

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Create Journal Voucher with lines and attachments.
        
        Expected payload:
        {
            "journal_voucher": { voucher_date, voucher_type, narration, ... },
            "voucher_lines": [ { ledger_account_id, entry_type, amount, ... }, ... ],
            "attachments": [ { attachment_name, attachment_path }, ... ]
        }
        
        Validates:
        - Voucher header data
        - Line items (at least 2 lines required for balanced entry)
        - Total Debit = Total Credit
        """
        given_data = request.data
        errors = {}

        # Extract and validate Journal Voucher data
        journal_voucher_data = given_data.pop('journal_voucher', None)
        if not journal_voucher_data:
            return build_response(0, "journal_voucher data is mandatory", [], status.HTTP_400_BAD_REQUEST)
        
        voucher_error = validate_payload_data(self, journal_voucher_data, JournalVoucherSerializer)
        if voucher_error:
            errors["journal_voucher"] = voucher_error

        # Extract and validate voucher lines
        lines_data = given_data.pop('voucher_lines', [])
        
        # ---------------- CLEAN EMPTY VOUCHER LINES ---------------- #
        # Remove blank/empty payloads created by frontend (5-10 default rows)
        # Similar to Sale Order pattern - filter out lines without ledger_account_id or amount
        if lines_data:
            lines_data = [
                line for line in lines_data
                if line.get("ledger_account_id") and line.get("amount") and Decimal(str(line.get("amount", 0))) > 0
            ]
        # ---------------------------------------------------------- #
        
        if not lines_data or len(lines_data) < 2:
            errors["voucher_lines"] = "At least 2 line items are required for a balanced journal entry"
        else:
            lines_error = validate_multiple_data(self, lines_data, JournalVoucherLineSerializer, ['journal_voucher_id'])
            if lines_error:
                errors["voucher_lines"] = lines_error

        # Validate Debit = Credit (Golden Rule of Accounting)
        if lines_data and not errors.get("voucher_lines"):
            total_debit = sum(Decimal(str(line.get('amount', 0))) for line in lines_data if line.get('entry_type') == 'Debit')
            total_credit = sum(Decimal(str(line.get('amount', 0))) for line in lines_data if line.get('entry_type') == 'Credit')
            
            if total_debit != total_credit:
                errors["balance"] = f"Total Debit (₹{total_debit}) must equal Total Credit (₹{total_credit})"

        # Extract and validate attachments
        attachments_data = given_data.pop('attachments', [])
        if attachments_data:
            attachments_error = validate_multiple_data(self, attachments_data, JournalVoucherAttachmentSerializer, ['journal_voucher_id'])
            if attachments_error:
                errors["attachments"] = attachments_error

        # Return validation errors if any
        if errors:
            return build_response(0, "ValidationError", errors, status.HTTP_400_BAD_REQUEST)

        # Calculate totals
        total_debit = sum(Decimal(str(line.get('amount', 0))) for line in lines_data if line.get('entry_type') == 'Debit')
        total_credit = sum(Decimal(str(line.get('amount', 0))) for line in lines_data if line.get('entry_type') == 'Credit')
        
        # Set totals in voucher data
        journal_voucher_data['total_debit'] = total_debit
        journal_voucher_data['total_credit'] = total_credit

        # Create Journal Voucher
        new_voucher = generic_data_creation(self, [journal_voucher_data], JournalVoucherSerializer)[0]
        voucher_id = new_voucher.get("journal_voucher_id", None)

        # Create voucher lines
        new_lines = []
        if lines_data:
            new_lines = generic_data_creation(self, lines_data, JournalVoucherLineSerializer, {'journal_voucher_id': voucher_id})

        # Create attachments
        new_attachments = []
        if attachments_data:
            new_attachments = generic_data_creation(self, attachments_data, JournalVoucherAttachmentSerializer, {'journal_voucher_id': voucher_id})

        custom_data = {
            "journal_voucher": new_voucher,
            "voucher_lines": new_lines,
            "attachments": new_attachments,
        }
        
        logger.info(f"Journal Voucher created: {new_voucher.get('voucher_no')}")
        return build_response(1, "Record created successfully", custom_data, status.HTTP_201_CREATED)

    @transaction.atomic
    def put(self, request, pk, *args, **kwargs):
        """PUT Handler - Update existing Journal Voucher"""
        return self.update(request, pk, *args, **kwargs)

    @transaction.atomic
    def update(self, request, pk, *args, **kwargs):
        """
        Update Journal Voucher with lines and attachments.
        
        Expected payload same as POST.
        Supports partial updates of lines (add/update/delete).
        """
        given_data = request.data
        errors = {}

        # Validate Journal Voucher data
        journal_voucher_data = given_data.pop('journal_voucher', None)
        if journal_voucher_data:
            journal_voucher_data['journal_voucher_id'] = pk
            instance = JournalVoucher.objects.get(pk=pk)
            serializer = JournalVoucherSerializer(instance, data=journal_voucher_data, partial=False)
            if not serializer.is_valid():
                errors["journal_voucher"] = serializer.errors
        else:
            return build_response(0, "journal_voucher data is required", [], status.HTTP_400_BAD_REQUEST)

        # Validate voucher lines
        lines_data = given_data.pop('voucher_lines', [])
        
        # ---------------- CLEAN EMPTY VOUCHER LINES ---------------- #
        # Remove blank/empty payloads created by frontend (5-10 default rows)
        # Similar to Sale Order pattern - filter out lines without ledger_account_id or amount
        if lines_data:
            lines_data = [
                line for line in lines_data
                if line.get("ledger_account_id") and line.get("amount") and Decimal(str(line.get("amount", 0))) > 0
            ]
        # ---------------------------------------------------------- #
        
        if lines_data:
            lines_error = validate_multiple_data(self, lines_data, JournalVoucherLineSerializer, [])
            if lines_error:
                errors["voucher_lines"] = lines_error

        # Validate Debit = Credit
        if lines_data and not errors.get("voucher_lines"):
            total_debit = sum(Decimal(str(line.get('amount', 0))) for line in lines_data if line.get('entry_type') == 'Debit')
            total_credit = sum(Decimal(str(line.get('amount', 0))) for line in lines_data if line.get('entry_type') == 'Credit')
            
            if total_debit != total_credit:
                errors["balance"] = f"Total Debit (₹{total_debit}) must equal Total Credit (₹{total_credit})"

        # Validate attachments
        attachments_data = given_data.pop('attachments', [])
        if attachments_data:
            attachments_error = validate_multiple_data(self, attachments_data, JournalVoucherAttachmentSerializer, [])
            if attachments_error:
                errors["attachments"] = attachments_error

        # Return validation errors if any
        if errors:
            return build_response(0, "ValidationError", errors, status.HTTP_400_BAD_REQUEST)

        # Update totals
        if lines_data:
            total_debit = sum(Decimal(str(line.get('amount', 0))) for line in lines_data if line.get('entry_type') == 'Debit')
            total_credit = sum(Decimal(str(line.get('amount', 0))) for line in lines_data if line.get('entry_type') == 'Credit')
            journal_voucher_data['total_debit'] = total_debit
            journal_voucher_data['total_credit'] = total_credit

        # Update Journal Voucher
        updated_voucher = update_multi_instances(
            self, pk, [journal_voucher_data], JournalVoucher, JournalVoucherSerializer, [],
            main_model_related_field='journal_voucher_id', current_model_pk_field='journal_voucher_id'
        )[0]

        # Update voucher lines
        updated_lines = []
        if lines_data:
            updated_lines = update_multi_instances(
                self, pk, lines_data, JournalVoucherLine, JournalVoucherLineSerializer,
                {'journal_voucher_id': pk},
                main_model_related_field='journal_voucher_id', current_model_pk_field='journal_voucher_line_id'
            )

        # Update attachments
        updated_attachments = []
        if attachments_data:
            updated_attachments = update_multi_instances(
                self, pk, attachments_data, JournalVoucherAttachment, JournalVoucherAttachmentSerializer,
                {'journal_voucher_id': pk},
                main_model_related_field='journal_voucher_id', current_model_pk_field='attachment_id'
            )

        custom_data = {
            "journal_voucher": updated_voucher,
            "voucher_lines": updated_lines,
            "attachments": updated_attachments,
        }
        
        logger.info(f"Journal Voucher updated: {updated_voucher.get('voucher_no')}")
        return build_response(1, "Records updated successfully", custom_data, status.HTTP_200_OK)

    @transaction.atomic
    def delete(self, request, pk, *args, **kwargs):
        """
        Soft delete Journal Voucher.
        Sets is_deleted = True instead of hard delete.
        Also soft-deletes corresponding JournalEntryLines (Account Ledger entries).
        """
        try:
            instance = self.get_object(pk)
            if instance is None:
                return build_response(0, "Record does not exist", [], status.HTTP_404_NOT_FOUND)
            
            # Check if voucher is already posted to ledger
            if instance.is_posted:
                return build_response(0, "Cannot delete a posted voucher. Please reverse it first.", [], status.HTTP_400_BAD_REQUEST)
            
            # Soft delete the voucher (signal will handle JournalEntryLines deletion)
            instance.is_deleted = True
            instance.save()
            
            # Explicitly soft-delete corresponding JournalEntryLines for safety
            # This ensures Account Ledger entries are marked as deleted
            from apps.finance.signals import delete_ledger_entries_for_voucher
            deleted_count = delete_ledger_entries_for_voucher(instance.voucher_no)
            
            logger.info(f"Journal Voucher deleted: {instance.voucher_no}, Ledger entries deleted: {deleted_count}")
            return build_response(1, "Record deleted successfully", [], status.HTTP_200_OK)
        except Exception as e:
            logger.error(f"Error deleting Journal Voucher: {str(e)}")
            return build_response(0, f"Error deleting record: {str(e)}", [], status.HTTP_400_BAD_REQUEST)



class JournalVoucherLineViewSet(viewsets.ModelViewSet):
    """
    ViewSet for individual Journal Voucher Line operations.
    Useful for getting lines by voucher_id or individual line operations.
    """
    queryset = JournalVoucherLine.objects.all().order_by('-created_at')
    serializer_class = JournalVoucherLineSerializer
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_class = JournalVoucherLineFilter
    ordering_fields = ['created_at', 'entry_type', 'amount']
    
    # Log actions
    log_actions = True
    log_module_name = "Journal Voucher Lines"
    log_pk_field = "journal_voucher_line_id"
    log_display_field = "remark"

    def list(self, request, *args, **kwargs):
        return list_filtered_objects(self, request, JournalVoucherLine, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        return create_instance(self, request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        return update_instance(self, request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return build_response(1, "Record deleted successfully", [], status.HTTP_200_OK)


class JournalVoucherPostView(APIView):
    """
    Post Journal Voucher to Ledger.
    Creates corresponding JournalEntryLines for ledger reports.
    
    This is called when user clicks "Post" to make the voucher final.
    """
    
    @transaction.atomic
    def post(self, request, pk, *args, **kwargs):
        """
        Post voucher to ledger - creates JournalEntryLines
        """
        try:
            voucher = JournalVoucher.objects.get(pk=pk)
            
            if voucher.is_posted:
                return build_response(0, "Voucher already posted", [], status.HTTP_400_BAD_REQUEST)
            
            if voucher.is_deleted:
                return build_response(0, "Cannot post a deleted voucher", [], status.HTTP_400_BAD_REQUEST)
            
            # Get voucher lines
            voucher_lines = JournalVoucherLine.objects.filter(journal_voucher_id=pk)
            
            if not voucher_lines.exists():
                return build_response(0, "No line items found in voucher", [], status.HTTP_400_BAD_REQUEST)
            
            # Create JournalEntry for this voucher
            journal_entry = JournalEntry.objects.create(
                entry_date=voucher.voucher_date,
                voucher_type='CommonVoucher',
                reference=voucher.reference_no,
                description=voucher.narration
            )
            
            # Create JournalEntryLines for each voucher line
            for line in voucher_lines:
                JournalEntryLines.objects.create(
                    journal_entry_id=journal_entry,
                    ledger_account_id=line.ledger_account_id,
                    voucher_no=voucher.voucher_no,
                    debit=line.amount if line.entry_type == 'Debit' else Decimal('0.00'),
                    credit=line.amount if line.entry_type == 'Credit' else Decimal('0.00'),
                    description=line.remark or voucher.narration,
                    customer_id=line.customer_id,
                    vendor_id=line.vendor_id
                )
            
            # Mark voucher as posted
            voucher.is_posted = True
            voucher.save()
            
            logger.info(f"Journal Voucher posted to ledger: {voucher.voucher_no}")
            return build_response(1, "Voucher posted to ledger successfully", {"voucher_no": voucher.voucher_no, "journal_entry_id": str(journal_entry.journal_entry_id)}, status.HTTP_200_OK)
            
        except JournalVoucher.DoesNotExist:
            return build_response(0, "Voucher not found", [], status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error posting voucher: {str(e)}")
            return build_response(0, f"Error posting voucher: {str(e)}", [], status.HTTP_500_INTERNAL_SERVER_ERROR)

#No Need This Api

# class PullFromExpenseClaimView(APIView):
#     """
#     Pull expense claim data to populate Journal Voucher.
#     Used for "Pull from Expense Claim" feature in UI.
#     """
    
#     def get(self, request, expense_claim_id, *args, **kwargs):
#         """
#         Get expense claim data formatted for Journal Voucher creation.
#         Returns pre-populated voucher lines.
#         """
#         try:
#             expense_claim = ExpenseClaim.objects.get(pk=expense_claim_id)
            
#             if expense_claim.status != 'Approved':
#                 return build_response(0, "Only approved expense claims can be pulled", [], status.HTTP_400_BAD_REQUEST)
            
#             # Get expense items for this claim
#             expense_items = ExpenseItem.objects.filter(expense_claim_id=expense_claim_id)
            
#             # Prepare voucher lines
#             voucher_lines = []
#             total_amount = Decimal('0.00')
            
#             for item in expense_items:
#                 voucher_lines.append({
#                     "ledger_account_id": str(item.ledger_account_id_id) if item.ledger_account_id else None,
#                     "entry_type": "Debit",
#                     "amount": str(item.amount),
#                     "remark": item.description,
#                     "employee_id": str(expense_claim.employee_id_id) if expense_claim.employee_id else None
#                 })
#                 total_amount += item.amount
            
#             # Add credit entry for employee reimbursement
#             voucher_lines.append({
#                 "ledger_account_id": None,  # To be selected by user (Cash/Bank account)
#                 "entry_type": "Credit",
#                 "amount": str(total_amount),
#                 "remark": f"Reimbursement for expense claim",
#                 "employee_id": str(expense_claim.employee_id_id) if expense_claim.employee_id else None
#             })
            
#             response_data = {
#                 "expense_claim": {
#                     "expense_claim_id": str(expense_claim.expense_claim_id),
#                     "employee_id": str(expense_claim.employee_id_id) if expense_claim.employee_id else None,
#                     "claim_date": str(expense_claim.claim_date),
#                     "total_amount": str(expense_claim.total_amount),
#                     "description": expense_claim.description
#                 },
#                 "suggested_voucher_lines": voucher_lines,
#                 "total_debit": str(total_amount),
#                 "total_credit": str(total_amount)
#             }
            
#             return build_response(1, "Expense claim data retrieved", response_data, status.HTTP_200_OK)
            
#         except ExpenseClaim.DoesNotExist:
#             return build_response(0, "Expense claim not found", [], status.HTTP_404_NOT_FOUND)
#         except Exception as e:
#             logger.error(f"Error pulling expense claim: {str(e)}")
#             return build_response(0, f"Error: {str(e)}", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class AccountCityListAPIView(APIView):
    def get(self, request):
        account_type = request.query_params.get('type')

        if account_type == 'customer':
            qs = CustomerAddresses.objects.filter(city_id__isnull=False)

        elif account_type == 'vendor':
            qs = VendorAddress.objects.filter(city_id__isnull=False)
            
        # ✅ NEW: GENERAL → NO CITY FILTER
        elif account_type == 'general':
            return Response(
                {"message": "General ledger has no city filter", "data": []},
                status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"message": "Invalid account type", "data": []},
                status=status.HTTP_400_BAD_REQUEST
            )

        cities = (
            qs.values(
                'city_id',
                'city_id__city_name'
            )
            .distinct()
            .order_by('city_id__city_name')
        )

        return Response({
            "data": [
                {
                    "label": c['city_id__city_name'],
                    "value": c['city_id']
                }
                for c in cities
            ]
        })        


# ======================================
# JOURNAL BOOK REPORT VIEW
# ======================================

class JournalBookReportView(APIView):
    """
    Journal Book Report AP
    This report displays all journal vouchers with their line items in a format
    similar to a 
    """
    
    def get(self, request, *args, **kwargs):
        """
        GET Handler - Returns Journal Book Report with all vouchers and lines.
        """
        try:
            # Get pagination parameters
            page = int(request.query_params.get('page', 1))
            limit = int(request.query_params.get('limit', 100))
            
            # Get date range parameters
            from_date = request.query_params.get('voucher_date_after', None)
            to_date = request.query_params.get('voucher_date_before', None)
            
            # Base queryset - only non-deleted vouchers, ordered by date desc then voucher_no
            queryset = JournalVoucher.objects.filter(
                is_deleted=False
            ).order_by('-voucher_date', '-voucher_no')
            
            # Apply filters using JournalBookReportFilter
            if request.query_params:
                filterset = JournalBookReportFilter(request.GET, queryset=queryset)
                if filterset.is_valid():
                    queryset = filterset.qs
            
            # Get total count before pagination
            total_count = queryset.count()
            
            # Calculate grand totals from all filtered records
            totals = queryset.aggregate(
                grand_total_debit=Coalesce(Sum('total_debit'), Decimal('0.00')),
                grand_total_credit=Coalesce(Sum('total_credit'), Decimal('0.00'))
            )
            
            # Apply pagination
            start_index = (page - 1) * limit
            end_index = start_index + limit
            paginated_queryset = queryset[start_index:end_index]
            
            # Build response data
            report_data = []
            
            for voucher in paginated_queryset:
                # Get all lines for this voucher
                voucher_lines = JournalVoucherLine.objects.filter(
                    journal_voucher_id=voucher.journal_voucher_id
                ).select_related(
                    'ledger_account_id', 
                    'customer_id', 
                    'vendor_id',
                    'employee_id'
                ).order_by('entry_type', 'created_at')
                
                # Build line data
                lines_data = []
                for line in voucher_lines:
                    # Get ledger account details
                    ledger_name = ''
                    ledger_group = ''
                    if line.ledger_account_id:
                        ledger_name = line.ledger_account_id.name or ''
                        # Get account group if available
                        if hasattr(line.ledger_account_id, 'account_group_id') and line.ledger_account_id.account_group_id:
                            ledger_group = line.ledger_account_id.account_group_id.group_name or ''
                        elif hasattr(line.ledger_account_id, 'account_type'):
                            ledger_group = line.ledger_account_id.account_type or ''
                    
                    # Get party name (customer, vendor, or employee)
                    party_name = None
                    if line.customer_id:
                        party_name = line.customer_id.name or ''
                    elif line.vendor_id:
                        party_name = line.vendor_id.name or ''
                    elif line.employee_id:
                        party_name = f"{line.employee_id.first_name or ''} {line.employee_id.last_name or ''}".strip()
                    
                    line_data = {
                        'ledger_account_name': ledger_name,
                        'ledger_group': ledger_group,
                        'party_name': party_name,
                        'entry_type': line.entry_type,
                        'debit': line.amount if line.entry_type == 'Debit' else Decimal('0.00'),
                        'credit': line.amount if line.entry_type == 'Credit' else Decimal('0.00'),
                        'remark': line.remark,
                        'bill_no': line.bill_no,
                        'tds_applicable': line.tds_applicable,
                        'tds_amount': line.tds_amount,
                    }
                    lines_data.append(line_data)
                
                # Build particulars text (similar to AlignBooks format)
                particulars = self._build_particulars(lines_data, voucher.narration)
                
                voucher_data = {
                    'journal_voucher_id': str(voucher.journal_voucher_id),
                    'voucher_no': voucher.voucher_no,
                    'voucher_date': voucher.voucher_date,
                    'voucher_type': voucher.voucher_type,
                    'narration': voucher.narration,
                    'reference_no': voucher.reference_no,
                    'is_posted': voucher.is_posted,
                    'total_debit': voucher.total_debit,
                    'total_credit': voucher.total_credit,
                    'lines': lines_data,
                    'particulars': particulars,
                }
                report_data.append(voucher_data)
            
            # Build summary
            summary = {
                'total_vouchers': total_count,
                'grand_total_debit': totals['grand_total_debit'],
                'grand_total_credit': totals['grand_total_credit'],
                'from_date': from_date,
                'to_date': to_date,
                'page': page,
                'limit': limit,
                'total_pages': (total_count + limit - 1) // limit if limit > 0 else 1
            }
            
            response_data = {
                'count': len(report_data),
                'message': 'Success',
                'data': report_data,
                'summary': summary,
                'page': page,
                'limit': limit,
                'totalCount': total_count
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error generating Journal Book Report: {str(e)}")
            return build_response(0, f"Error generating report: {str(e)}", [], status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def _build_particulars(self, lines_data, narration):
        """
        Build particulars text similar to AlignBooks format.
        
        Format for each line:
        Ledger Group (Bold)
        Account/Party Name
        (Being Journal Entry LEDGER## Type ₹Amount LEDGER## Type ₹Amount)
        """
        particulars_list = []
        
        # First, build the narration string that will be added to each line
        narration_parts = []
        for line in lines_data:
            ledger_name = line.get('ledger_account_name', '') or ''
            party_name = line.get('party_name', '')
            entry_type = line.get('entry_type', '')
            amount = line.get('debit', 0) if entry_type == 'Debit' else line.get('credit', 0)
            
            # Format amount with commas
            formatted_amount = f"₹{amount:,.2f}"
            
            if party_name:
                narration_parts.append(f"{ledger_name} [ {party_name}]## {entry_type} {formatted_amount}")
            elif ledger_name:
                narration_parts.append(f"{ledger_name}## {entry_type} {formatted_amount}")
        
        # Build the common narration text for all lines
        auto_narration = f"(Being Journal Entry {' '.join(narration_parts)})"
        
        # If user provided custom narration, use it; otherwise use auto-generated
        if narration and narration.strip():
            full_narration = f"(Being Journal Entry {narration})"
        else:
            full_narration = auto_narration
        
        # Now build each line's particulars with narration included
        for line in lines_data:
            ledger_group = line.get('ledger_group', '') or ''
            ledger_name = line.get('ledger_account_name', '') or ''
            party_name = line.get('party_name', '')
            entry_type = line.get('entry_type', '')
            amount = line.get('debit', 0) if entry_type == 'Debit' else line.get('credit', 0)
            
            # Build display text in AlignBooks format:
            # Line 1: Ledger Group (if exists)
            # Line 2: Account Name [Party Name]
            # Line 3: (Being Journal Entry...)
            
            display_lines = []
            
            # Add ledger group if exists
            if ledger_group:
                display_lines.append(ledger_group)
            
            # Add account/party name
            if party_name:
                display_lines.append(f"{ledger_name} [ {party_name}]")
            else:
                display_lines.append(ledger_name)
            
            # Add narration
            display_lines.append(full_narration)
            
            display_text = '\n'.join(display_lines)
            
            particulars_list.append({
                'text': display_text,
                'entry_type': entry_type,
                'amount': float(amount) if amount else 0,
                'ledger_group': ledger_group,
                'ledger_name': ledger_name,
                'party_name': party_name,
                'narration': full_narration
            })
        
        return particulars_list
