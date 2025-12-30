from django_filters import rest_framework as filters
from apps.customer.models import CustomerAddresses
from apps.finance.models import BankAccount, Budget, ChartOfAccounts, ExpenseClaim, ExpenseItem, FinancialReport, JournalEntry, JournalEntryLines, PaymentTransaction, TaxConfiguration
from apps.vendor.models import VendorAddress
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
from django.db.models import Q
logger = logging.getLogger(__name__)
from django_filters import FilterSet, ChoiceFilter ,DateFromToRangeFilter


class BankAccountFilter(filters.FilterSet):
    account_name = filters.CharFilter(lookup_expr='icontains')
    account_number = filters.CharFilter(lookup_expr='icontains')
    bank_name = filters.CharFilter(lookup_expr='icontains')
    branch_name = filters.CharFilter(lookup_expr='icontains')
    account_type = filters.ChoiceFilter(field_name='account_type',choices=[('Current', 'Current'),('Savings', 'Savings')])
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = BankAccount 
        #do not change "account_name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['account_name','account_number','bank_name','branch_name','account_type','created_at','period_name','s','sort','page','limit']


class ChartOfAccountsFilter(filters.FilterSet):
    account_id = filters.CharFilter(method=filter_uuid)
    account_code = filters.CharFilter(lookup_expr='icontains')
    account_name = filters.CharFilter(lookup_expr='icontains')
    account_type = filters.ChoiceFilter(choices=[('Asset', 'Asset'),('Equity', 'Equity'), ('Expense', 'Expense'), ('Liability', 'Liability'), ('Revenue', 'Revenue')])
    parent_account_id = filters.CharFilter(field_name='parent_account_id__account_name', lookup_expr='icontains')
    bank_account_id = filters.CharFilter(field_name='bank_account_id__bank_name', lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = ChartOfAccounts 
        #do not change "account_code",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['account_code','account_name','account_type','parent_account_id','bank_account_id','created_at','period_name','s','sort','page','limit']
        

class JournalEntryFilter(filters.FilterSet):
    entry_date = filters.DateFromToRangeFilter()
    reference = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = JournalEntry 
        #do not change "entry_date",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['entry_date','reference','description','created_at','period_name','s','sort','page','limit']


class PaymentTransactionFilter(filters.FilterSet):
    invoice_id = filters.CharFilter(lookup_expr='icontains')
    order_type = filters.ChoiceFilter(choices=[('Purchase', 'Purchase'),('Sale', 'Sale')])
    payment_date = filters.DateFromToRangeFilter()
    payment_method = filters.ChoiceFilter(field_name='payment_method',choices=[('Bank Transfer', 'Bank Transfer'),('Cash', 'Cash'),('Cheque', 'Cheque'),('Credit Card', 'Credit Card')])
    payment_status = filters.ChoiceFilter(field_name='payment_status',choices=[('Completed', 'Completed'),('Failed', 'Failed'),('Pending', 'Pending')])
    amount = filters.RangeFilter()
    reference_number = filters.CharFilter(lookup_expr='icontains')
    currency = filters.CharFilter(lookup_expr='icontains')
    transaction_type = filters.ChoiceFilter(choices=[('Credit', 'Credit'),('Debit', 'Debit')])
    notes = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = PaymentTransaction 
        #do not change "invoice_id",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['invoice_id','order_type','payment_date','payment_method','payment_status','amount','reference_number','currency','transaction_type','notes','created_at','period_name','s','sort','page','limit']


class TaxConfigurationFilter(filters.FilterSet):
    tax_name = filters.CharFilter(lookup_expr='icontains')
    tax_rate = filters.RangeFilter()
    tax_type = filters.ChoiceFilter(choices=TaxConfiguration.TAX_TYPE_CHOICES)
    is_active = filters.BooleanFilter()
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = TaxConfiguration 
        #do not change "tax_name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['tax_name','tax_rate','tax_type','is_active','created_at','period_name','s','sort','page','limit']


class BudgetFilter(filters.FilterSet):
    account_id = filters.CharFilter(field_name='account_id__account_name', lookup_expr='iexact')
    fiscal_year = filters.NumberFilter()
    allocated_amount = filters.RangeFilter()
    spent_amount = filters.RangeFilter()
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = Budget 
        #do not change "account_id",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['account_id','fiscal_year','allocated_amount','spent_amount','created_at','period_name','s','sort','page','limit']


class ExpenseClaimFilter(filters.FilterSet):
    employee_id = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='iexact')
    claim_date = filters.DateFromToRangeFilter()
    description = filters.CharFilter(lookup_expr='icontains')
    total_amount = filters.RangeFilter()
    status = filters.ChoiceFilter(choices=ExpenseClaim.STATUS_CHOICES)
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = ExpenseClaim 
        #do not change "employee_id",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['employee_id','claim_date','description','total_amount','status','created_at','period_name','s','sort','page','limit']


class FinancialReportFilter(filters.FilterSet):
    report_name = filters.CharFilter(lookup_expr='icontains')
    report_type = filters.ChoiceFilter(choices=FinancialReport.REPORT_TYPE_CHOICES,field_name='report_type')
    generated_at = filters.DateFromToRangeFilter()
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = FinancialReport 
        #do not change "report_name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['report_name','report_type','generated_at','created_at','period_name','s','sort','page','limit']


class JournalEntryLineFilter(filters.FilterSet):
    ledger_account_id = filters.UUIDFilter(field_name='ledger_account_id__ledger_account_id', lookup_expr='exact')
    date = filters.DateFromToRangeFilter(field_name='journal_entry_id__entry_date')  # Fixed
    account = filters.CharFilter(field_name='account_id__account_name', lookup_expr='icontains')  
    reference = filters.CharFilter(field_name='journal_entry_id__reference', lookup_expr='icontains')  # Fixed
    debit = filters.NumberFilter(field_name='debit')
    credit = filters.NumberFilter(field_name='credit')
    description = filters.CharFilter(field_name='description',lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()        
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

 
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)

    class Meta:
        model = JournalEntryLines
        fields = ['date', 'account', 'reference','ledger_account_id', 'debit', 'credit', 'description','created_at','s','sort','page','limit']

class JournalEntryLinesListFilter(filters.FilterSet):
    """Filter for Journal Entry Lines when listed by customer or vendor ID"""
    # account_id = filters.CharFilter(method=filter_uuid)
    # account = filters.CharFilter(field_name='account_id__account_name', lookup_expr='icontains')
    ledger_account_id = filters.CharFilter(method=filter_uuid)
    ledger_account = filters.CharFilter(field_name='ledger_account_id__name', lookup_expr='icontains')
    voucher_no = filters.CharFilter(lookup_expr='icontains')
    debit = filters.RangeFilter()
    voucher_no = filters.CharFilter( lookup_expr='icontains')
    debit = filters.RangeFilter()
    credit = filters.RangeFilter()
    balance = filters.RangeFilter()
    description = filters.CharFilter(lookup_expr='icontains')
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    city = filters.CharFilter(method='filter_by_city')
    # Standard filter methods
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    def filter_by_city(self, queryset, name, value):
        """
        Apply city filter based on active ledger context
        (customer / vendor only)
        """

        # Get active PK from URL
        # pk = self.request.parser_context.get('kwargs', {}).get('pk')
        pk = self.request.resolver_match.kwargs.get('pk')

        if pk == 'customer_id':
            return queryset.filter(
                customer_id__in=CustomerAddresses.objects.filter(
                    city_id=value
                ).values_list('customer_id', flat=True)
            )

        elif pk == 'vendor_id':
            return queryset.filter(
                vendor_id__in=VendorAddress.objects.filter(
                    city_id=value
                ).values_list('vendor_id', flat=True)
            )

        # ledger_account_id → city NOT applicable
        return queryset



    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = JournalEntryLines
        fields = ['ledger_account_id', 'ledger_account',  'voucher_no', 'debit', 'credit', 'description', 'balance', 'created_at', 'city',  's', 'sort', 'page', 'limit']

class TrialBalanceReportFilter(filters.FilterSet):
    start_date = filters.DateFilter(field_name='journal_entry_lines__journal_entry_id__entry_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='journal_entry_lines__journal_entry_id__entry_date', lookup_expr='lte')
    account_type = filters.CharFilter(field_name='account_type')
    account_code = filters.CharFilter(field_name='account_code', lookup_expr='icontains')
    account_name = filters.CharFilter(field_name='account_name', lookup_expr='icontains')
    total_debit = filters.NumberFilter()
    total_credit = filters.NumberFilter()
    balance = filters.NumberFilter()
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = ChartOfAccounts
        fields = ['start_date', 'end_date', 'account_type', 'account_code', 
                 'account_name', 'total_debit', 'total_credit', 'balance',
                 's', 'sort', 'page', 'limit']

class GeneralLedgerReportFilter(filters.FilterSet):
    """Filter for General Ledger Report that shows all financial transactions across all accounts."""
    account_id = filters.CharFilter(method=filter_uuid)
    account_name = filters.CharFilter(field_name='account_id__account_name', lookup_expr='icontains')
    start_date = filters.DateFilter(field_name='journal_entry_id__entry_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='journal_entry_id__entry_date', lookup_expr='lte')
    reference_number = filters.CharFilter(field_name='journal_entry_id__reference', lookup_expr='icontains')
    min_amount = filters.NumberFilter(method='filter_min_amount')
    max_amount = filters.NumberFilter(method='filter_max_amount')
    description = filters.CharFilter(field_name='description', lookup_expr='icontains')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_min_amount(self, queryset, name, value):
        """Filter transactions with amount greater than or equal to the specified value"""
        from django.db.models import Q
        if value:
            return queryset.filter(Q(debit__gte=value) | Q(credit__gte=value))
        return queryset

    def filter_max_amount(self, queryset, name, value):
        """Filter transactions with amount less than or equal to the specified value"""
        from django.db.models import Q
        if value:
            return queryset.filter(Q(debit__lte=value) | Q(credit__lte=value))
        return queryset

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = JournalEntryLines
        fields = ['account_id', 'account_name', 'start_date', 'end_date', 'reference_number', 'min_amount', 'max_amount', 'description', 's', 'sort', 'page', 'limit']

class ProfitLossReportFilter(filters.FilterSet):
    """Filter for Profit and Loss Report showing revenue, expenses and profit/loss."""
    start_date = filters.DateFilter(field_name='journal_entry_lines__journal_entry_id__entry_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='journal_entry_lines__journal_entry_id__entry_date', lookup_expr='lte')
    account_type = filters.MultipleChoiceFilter(
        choices=[('Revenue', 'Revenue'), ('Expense', 'Expense')],
        field_name='account_type'
    )
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = ChartOfAccounts
        fields = ['start_date', 'end_date', 'account_type', 's', 'sort', 'page', 'limit']


class BalanceSheetReportFilter(filters.FilterSet):
    """Filter for Balance Sheet Report showing assets, liabilities and equity."""
    start_date = filters.DateFilter(field_name='journal_entry_lines__journal_entry_id__entry_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='journal_entry_lines__journal_entry_id__entry_date', lookup_expr='lte')
    account_type = filters.MultipleChoiceFilter(
        choices=[('Asset', 'Asset'), ('Liability', 'Liability'), ('Equity', 'Equity')],
        field_name='account_type'
    )
    account_code = filters.CharFilter(field_name='account_code', lookup_expr='icontains')
    account_name = filters.CharFilter(field_name='account_name', lookup_expr='icontains')
    total_debit = filters.NumberFilter()
    total_credit = filters.NumberFilter()
    balance = filters.NumberFilter()
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = ChartOfAccounts
        fields = ['start_date', 'end_date', 'account_type', 'account_code', 'account_name',
                 'total_debit', 'total_credit', 'balance', 's', 'sort', 'page', 'limit']

class CashFlowReportFilter(filters.FilterSet):
    """Filter for Cash Flow Statement showing inflow and outflow of cash."""
    start_date = filters.DateFilter(field_name='journal_entry_lines__journal_entry_id__entry_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='journal_entry_lines__journal_entry_id__entry_date', lookup_expr='lte')
    activity_type = filters.ChoiceFilter(
        choices=[('Operating', 'Operating'), ('Investing', 'Investing'), ('Financing', 'Financing')],
        method='filter_by_activity_type'
    )
    account_code = filters.CharFilter(field_name='account_code', lookup_expr='icontains')
    account_name = filters.CharFilter(field_name='account_name', lookup_expr='icontains')
    account_type = filters.CharFilter(field_name='account_type', lookup_expr='iexact')
    cash_inflow = filters.NumberFilter()
    cash_outflow = filters.NumberFilter()
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_activity_type(self, queryset, name, value):
        """Filter transactions by cash flow activity type"""
        if value == 'Operating':
            return queryset.filter(account_type__in=['Revenue', 'Expense'])
        elif value == 'Investing':
            return queryset.filter(account_type='Asset')
        elif value == 'Financing':
            return queryset.filter(account_type__in=['Liability', 'Equity'])
        return queryset
        
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = ChartOfAccounts
        fields = ['start_date', 'end_date', 'activity_type', 'account_code', 'account_name', 'account_type', 'cash_inflow', 'cash_outflow', 's', 'sort', 'page', 'limit']

class AgingReportFilter(filters.FilterSet):
    """Filter for Aging Report showing pending payments by age categories."""
    payment_date = filters.DateFromToRangeFilter()
    payment_status = filters.ChoiceFilter(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Failed', 'Failed')])
    due_days = filters.RangeFilter()
    order_type = filters.ChoiceFilter(choices=[('Purchase', 'Purchase'), ('Sale', 'Sale')])
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = PaymentTransaction
        fields = ['payment_date', 'payment_status', 'due_days', 'order_type', 'min_amount', 'max_amount', 's', 'sort', 'page', 'limit']

class BankReconciliationReportFilter(filters.FilterSet):
    """Filter for Bank Reconciliation Report comparing bank statement with ledger balance."""
    bank_name = filters.CharFilter(field_name='bank_name', lookup_expr='icontains')
    account_number = filters.CharFilter(field_name='account_number', lookup_expr='icontains')
    account_name = filters.CharFilter(field_name='account_name', lookup_expr='icontains')
    min_balance = filters.NumberFilter(field_name='balance', lookup_expr='gte')
    max_balance = filters.NumberFilter(field_name='balance', lookup_expr='lte')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = BankAccount
        fields = ['bank_name', 'account_number', 'account_name', 'min_balance', 'max_balance', 's', 'sort', 'page', 'limit']

class JournalEntryReportFilter(filters.FilterSet):
    """Filter for Journal Entry Report showing all journal entries and their details."""
    entry_date = filters.DateFromToRangeFilter()
    reference = filters.CharFilter(lookup_expr='icontains')
    description = filters.CharFilter(lookup_expr='icontains')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = JournalEntry
        fields = ['entry_date', 'reference', 'description', 's', 'sort', 'page', 'limit']
        
        
# class ExpenseCategoryFilter(filters.FilterSet):
#     category_name = filters.CharFilter(lookup_expr='icontains')
#     description = filters.CharFilter(lookup_expr='icontains')
#     account_id = filters.CharFilter(field_name='account_id__account_name', lookup_expr='icontains')
#     is_active = filters.BooleanFilter()
#     created_at = filters.DateFromToRangeFilter()
#     period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
#     s = filters.CharFilter(method='filter_by_search', label="Search")
#     sort = filters.CharFilter(method='filter_by_sort', label="Sort")
#     page = filters.NumberFilter(method='filter_by_page', label="Page")
#     limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

#     def filter_by_period_name(self, queryset, name, value):
#         return filter_by_period_name(self, queryset, self.data, value)

#     def filter_by_search(self, queryset, name, value):
#         return filter_by_search(queryset, self, value)

#     def filter_by_sort(self, queryset, name, value):
#         return filter_by_sort(self, queryset, value)

#     def filter_by_page(self, queryset, name, value):
#         return filter_by_page(self, queryset, value)

#     def filter_by_limit(self, queryset, name, value):
#         return filter_by_limit(self, queryset, value)
    
#     class Meta:
#         model = ExpenseCategory
#         fields = ['category_name','description','account_id','is_active','created_at','period_name','s','sort','page','limit']

class ExpenseItemFilter(filters.FilterSet):
    expense_date = filters.DateFromToRangeFilter()
    description = filters.CharFilter(lookup_expr='icontains')
    amount = filters.RangeFilter()
    category_id = filters.CharFilter(field_name='category_id__category_name', lookup_expr='icontains')
    bank_account_id = filters.CharFilter(field_name='bank_account_id__bank_name', lookup_expr='icontains')
    vendor_id = filters.CharFilter(field_name='vendor_id__name', lookup_expr='icontains')
    employee_id = filters.CharFilter(field_name='employee_id__first_name', lookup_expr='icontains')
    expense_claim_id = filters.CharFilter(method=filter_uuid)
    status = filters.ChoiceFilter(choices=ExpenseItem.STATUS_CHOICES)
    payment_method = filters.CharFilter(lookup_expr='iexact')
    budget_id = filters.CharFilter(method=filter_uuid)
    is_taxable = filters.BooleanFilter()
    is_recurring = filters.BooleanFilter()
    recurring_frequency = filters.CharFilter(lookup_expr='iexact')
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    class Meta:
        model = ExpenseItem
        fields = ['expense_date','description','amount','category_id','bank_account_id','vendor_id','employee_id',
                 'expense_claim_id','status','payment_method','budget_id','is_taxable','is_recurring',
                 'recurring_frequency','created_at','period_name','s','sort','page','limit']

        
        