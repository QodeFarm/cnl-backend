from django_filters import rest_framework as filters
import uuid
from django.db.models import Q
from apps.customer.models import Customer, LedgerAccounts
from apps.sales.models import SaleInvoiceOrders
from apps.finance.models import JournalEntryLines, PaymentTransaction
from config.utils_methods import filter_uuid
from config.utils_filter_methods import PERIOD_NAME_CHOICES, filter_by_period_name, filter_by_search, filter_by_sort, filter_by_page, filter_by_limit, filter_by_simple_search
import logging
logger = logging.getLogger(__name__)

class LedgerAccountsFilters(filters.FilterSet):
    name = filters.CharFilter(lookup_expr='icontains')
    code = filters.CharFilter(lookup_expr='exact')
    inactive = filters.BooleanFilter()
    type = filters.CharFilter(lookup_expr='exact')
    account_no = filters.CharFilter(lookup_expr='exact')
    is_loan_account = filters.BooleanFilter()
    pan = filters.CharFilter(lookup_expr='exact')
    address = filters.CharFilter(lookup_expr='icontains')
    ledger_group_id = filters.CharFilter(field_name='ledger_group_id__name', lookup_expr='exact')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    created_at = filters.DateFromToRangeFilter()

    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value)

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = LedgerAccounts 
        fields = ['name','code','inactive','type','account_no','is_loan_account','pan','address','ledger_group_id','created_at','s', 'sort','page','limit']

class CustomerFilters(filters.FilterSet):
    identification = filters.CharFilter(lookup_expr='exact')
    contact_person = filters.CharFilter(lookup_expr='exact')
    cin = filters.CharFilter(lookup_expr='exact')
    pan = filters.CharFilter(lookup_expr='exact')
    tax_type = filters.CharFilter(lookup_expr='exact')
    ledger_account_id = filters.CharFilter(field_name='ledger_account_id__name', lookup_expr='exact')
    gst_category_id = filters.CharFilter(field_name='gst_category_id__name', lookup_expr='exact')
    max_credit_days = filters.RangeFilter(lookup_expr='exact')
    name = filters.CharFilter(lookup_expr='icontains')
    gst = filters.CharFilter(lookup_expr='icontains')
    is_deleted = filters.BooleanFilter()
    created_at = filters.DateFromToRangeFilter()
    period_name = filters.ChoiceFilter(choices=PERIOD_NAME_CHOICES, method='filter_by_period_name')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    search = filters.CharFilter(method='filter_by_search_dropdown', label="Simple Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    # Fields from CustomerAddress
    email = filters.CharFilter(field_name='customeraddresses__email', lookup_expr='icontains', label="Email")
    phone = filters.CharFilter(field_name='customeraddresses__phone', lookup_expr='icontains', label="Phone")
    city_id = filters.CharFilter(field_name='customeraddresses__city_id__city_name', lookup_expr='icontains', label="City")
    
    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value).distinct()

    def filter_by_search_dropdown(self, queryset, name, value):
        """Simple search for dropdown - searches name, print_name, code"""
        return filter_by_simple_search(queryset, value, ['name', 'print_name', 'code'])

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
        
    class Meta:
        model = Customer
        #do not change "name",it should remain as the 0th index. When using ?summary=true&page=1&limit=10, it will retrieve the results in descending order.
        fields = ['name','gst','ledger_account_id','created_at','email', 'phone', 'city_id','period_name', 'is_deleted', 's','search','sort','page','limit']

    
class CustomerAttachmentsFilters(filters.FilterSet):
    customer_id = filters.CharFilter(field_name='customer_id__name', lookup_expr='exact')
    attachment_name = filters.CharFilter(lookup_expr='exact')

class CustomerAddressesFilters(filters.FilterSet):
    customer_id = filters.CharFilter(method=filter_uuid)
    city_id = filters.CharFilter(field_name='city_id__city_name', lookup_expr='exact')
    state_id = filters.CharFilter(field_name='state_id__state_name', lookup_expr='exact')
    country_id = filters.CharFilter(field_name='country_id__country_name', lookup_expr='exact')
    pin_code = filters.CharFilter(lookup_expr='exact')
    phone = filters.CharFilter(lookup_expr='exact')
    email = filters.CharFilter(lookup_expr='exact')

    def filter_customer_id(self, queryset, name, value):
        try:
            uuid.UUID(value)
        except ValueError:
            # If the UUID is invalid, return an empty queryset
            return queryset.none()
        return queryset.filter(Q(bank_detail_id=value))
    
    
class CustomerSummaryReportFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    total_sales = filters.RangeFilter(field_name='total_sales')
    total_advance = filters.RangeFilter(field_name='total_advance')
    outstanding_payments = filters.RangeFilter(field_name='outstanding_payments')
    created_at = filters.DateFromToRangeFilter()
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value).distinct()

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = Customer
        fields = ['name', 'total_sales', 'total_advance', 'outstanding_payments', 's', 'sort', 'page', 'limit']   
        
class CustomerOrderHistoryReportFilter(filters.FilterSet):
    invoice_no = filters.CharFilter(field_name='invoice_no', lookup_expr='icontains')
    customer = filters.CharFilter(field_name='customer_id__name', lookup_expr='iexact')
    invoice_date = filters.DateFromToRangeFilter(field_name='invoice_date')
    total_amount = filters.RangeFilter(field_name='total_amount')
    status_name = filters.CharFilter(field_name='order_status_id', lookup_expr='iexact')
    created_at = filters.filters.DateFromToRangeFilter()

    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value).distinct()

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = SaleInvoiceOrders
        fields = ['invoice_no', 'customer', 'invoice_date', 'total_amount', 's', 'sort', 'page', 'limit'] 
        
class CustomerCreditLimitReportFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    credit_limit = filters.RangeFilter(field_name='credit_limit')
    credit_usage = filters.RangeFilter(field_name='credit_usage')
    remaining_credit = filters.RangeFilter(field_name='remaining_credit')
    created_at = filters.filters.DateFromToRangeFilter()

    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_period_name(self, queryset, name, value):
        return filter_by_period_name(self, queryset, self.data, value)
    
    def filter_by_search(self, queryset, name, value):
        return filter_by_search(queryset, self, value).distinct()

    def filter_by_sort(self, queryset, name, value):
        return filter_by_sort(self, queryset, value)

    def filter_by_page(self, queryset, name, value):
        return filter_by_page(self, queryset, value)

    def filter_by_limit(self, queryset, name, value):
        return filter_by_limit(self, queryset, value)
    
    class Meta:
        model = Customer
        fields = ['name', 'credit_limit', 'credit_usage', 'remaining_credit', 's', 'sort', 'page', 'limit']

class CustomerLedgerReportFilter(filters.FilterSet):
    """
    Filter for Customer Ledger Report with date range and transaction type filtering options.
    """
    customer_id = filters.CharFilter(method=filter_uuid)
    start_date = filters.DateFilter(field_name='journal_entry_id__entry_date', lookup_expr='gte')
    end_date = filters.DateFilter(field_name='journal_entry_id__entry_date', lookup_expr='lte')
    reference_number = filters.CharFilter(field_name='journal_entry_id__reference', lookup_expr='icontains')
    transaction_type = filters.CharFilter(method='filter_transaction_type')
    min_amount = filters.NumberFilter(method='filter_min_amount')
    max_amount = filters.NumberFilter(method='filter_max_amount')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")

    def filter_transaction_type(self, queryset, name, value):
        """Filter transactions by type based on reference number patterns"""
        if value.lower() == 'sale order':
            return queryset.filter(journal_entry_id__reference__startswith='SO-')
        elif value.lower() == 'sale invoice':
            return queryset.filter(journal_entry_id__reference__startswith='SO-INV')
        elif value.lower() == 'sale return':
            return queryset.filter(journal_entry_id__reference__startswith='SR-')
        elif value.lower() == 'credit note':
            return queryset.filter(journal_entry_id__reference__startswith='CN-')
        elif value.lower() == 'debit note':
            return queryset.filter(journal_entry_id__reference__startswith='DN-')
        elif value.lower() == 'receipt':
            return queryset.filter(journal_entry_id__reference__startswith='RCPT-')
        elif value.lower() == 'payment':
            return queryset.filter(journal_entry_id__reference__startswith='PMT-')
        return queryset

    def filter_min_amount(self, queryset, name, value):
        """Filter transactions with amount greater than or equal to the specified value"""
        if value:
            # Using Q objects to check both debit and credit
            return queryset.filter(Q(debit__gte=value) | Q(credit__gte=value))
        return queryset

    def filter_max_amount(self, queryset, name, value):
        """Filter transactions with amount less than or equal to the specified value"""
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
        fields = ['customer_id', 'start_date', 'end_date', 'reference_number', 
                'transaction_type', 'min_amount', 'max_amount', 's', 'sort', 'page', 'limit']

class CustomerOutstandingReportFilter(filters.FilterSet):
    """
    Simplified filter for Customer Outstanding Report that tracks pending payments.
    """
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')
    min_total_pending = filters.NumberFilter(field_name='total_pending', lookup_expr='gte')
    max_total_pending = filters.NumberFilter(field_name='total_pending', lookup_expr='lte')
    min_due_days = filters.NumberFilter(method='filter_by_min_due_days')
    s = filters.CharFilter(method='filter_by_search', label="Search")
    sort = filters.CharFilter(method='filter_by_sort', label="Sort")
    page = filters.NumberFilter(method='filter_by_page', label="Page")
    limit = filters.NumberFilter(method='filter_by_limit', label="Limit")
    
    def filter_by_min_due_days(self, queryset, name, value):
        """Filter customers with invoices outstanding for at least the specified number of days"""
        if value:
            from django.utils import timezone
            from datetime import timedelta
            cutoff_date = timezone.now().date() - timedelta(days=int(value))
            return queryset.filter(saleinvoiceorders__due_date__lte=cutoff_date)
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
        model = Customer
        fields = ['name', 'min_total_pending', 'max_total_pending', 'min_due_days',
                 's', 'sort', 'page', 'limit']

class CustomerPaymentReportFilter(filters.FilterSet):
    """
    Filter for Customer Payment Report showing payments received from customers.
    """
    invoice_id = filters.CharFilter(lookup_expr='icontains')
    payment_date_after = filters.DateFilter(field_name='payment_date', lookup_expr='gte')
    payment_date_before = filters.DateFilter(field_name='payment_date', lookup_expr='lte')
    payment_method = filters.CharFilter(lookup_expr='icontains')
    payment_status = filters.CharFilter(lookup_expr='iexact')
    min_amount = filters.NumberFilter(field_name='amount', lookup_expr='gte')
    max_amount = filters.NumberFilter(field_name='amount', lookup_expr='lte')
    reference_number = filters.CharFilter(lookup_expr='icontains')
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
        fields = ['invoice_id', 'payment_date_after', 'payment_date_before',
                 'payment_method', 'payment_status', 'min_amount', 'max_amount', 
                 'reference_number', 's', 'sort', 'page', 'limit']