from django_filters import rest_framework as filters
from apps.finance.models import BankAccount, Budget, ChartOfAccounts, ExpenseClaim, FinancialReport, JournalEntry, PaymentTransaction, TaxConfiguration
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit
import logging
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
